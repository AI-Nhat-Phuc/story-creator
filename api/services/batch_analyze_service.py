"""Service for batch analysis of stories using GPT.

Extracted from gpt_routes.py to separate business logic from route handlers,
following the project's service layer architecture.
"""

import json
from core.models import Entity, Location, Story
from generators import StoryLinker


class BatchAnalyzeService:
    """Handles batch GPT analysis of stories in a world.

    Processes stories in chronological order, carrying character and location
    context forward across stories so that recurring entities are reused rather
    than duplicated.
    """

    def __init__(self, gpt, storage):
        """Initialize the service.

        Args:
            gpt: GPTIntegration instance for making API calls
            storage: Storage instance for data persistence
        """
        self.gpt = gpt
        self.storage = storage

    def run(self, world_id, story_ids, progress_callback=None):
        """Analyze stories in a world and link extracted entities/locations.

        Args:
            world_id: World UUID to analyze stories in
            story_ids: List of story IDs to analyze. If empty, analyzes all
                       unlinked stories (those with no entities AND no locations).
            progress_callback: Optional callable(progress, total, current_title)
                               called before processing each story.

        Returns:
            dict with keys:
                analyzed_stories: list of per-story analysis results
                total_characters_found: int
                total_locations_found: int
                linked_count: int
                message: human-readable summary string
        """
        from ai.prompts import PromptTemplates

        # Load stories to process
        stories_data = self.storage.list_stories(world_id)
        if story_ids:
            stories_data = [s for s in stories_data if s.get('story_id') in story_ids]
        else:
            stories_data = [
                s for s in stories_data
                if not s.get('entities') and not s.get('locations')
            ]

        if not stories_data:
            return {
                'analyzed_stories': [],
                'total_characters_found': 0,
                'total_locations_found': 0,
                'linked_count': 0,
                'message': 'Không có câu chuyện nào cần phân tích'
            }

        # Sort by world_time year (ascending)
        stories_data.sort(key=lambda s: s.get('metadata', {}).get('world_time', {}).get('year', 0))
        total = len(stories_data)

        # Seed context with existing world entities and locations
        existing_entities = self.storage.list_entities(world_id)
        existing_locations = self.storage.list_locations(world_id)
        known_chars = [e.get('name', '') for e in existing_entities if e.get('name')]
        known_locs = [l.get('name', '') for l in existing_locations if l.get('name')]

        analyzed_results = []
        total_chars_found = 0
        total_locs_found = 0

        for idx, story_data in enumerate(stories_data):
            story_title = story_data.get('title', '')
            story_desc = story_data.get('content', '')
            story_genre = story_data.get('genre', '')
            story_id = story_data.get('story_id')

            if progress_callback:
                progress_callback(idx, total, story_title)

            # Build prompt with accumulated context
            known_chars_str = ', '.join(known_chars) if known_chars else '(chưa có)'
            known_locs_str = ', '.join(known_locs) if known_locs else '(chưa có)'
            prompt = PromptTemplates.BATCH_ANALYZE_STORY_ENTITIES_TEMPLATE.format(
                story_title=story_title or 'None',
                story_genre=story_genre or 'Unknown',
                story_description=story_desc,
                known_characters=known_chars_str,
                known_locations=known_locs_str
            )

            response = self.gpt.client.chat.completions.create(
                model=self.gpt.model,
                messages=[
                    {"role": "system", "content": PromptTemplates.TEXT_ANALYZER_SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=500,
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content.strip())
            characters = analysis.get('characters', [])
            locations_found = analysis.get('locations', [])

            # Resolve or create entities
            linked_entity_ids = self._resolve_entities(
                characters, world_id, existing_entities, known_chars
            )

            # Resolve or create locations
            linked_location_ids = self._resolve_locations(
                locations_found, world_id, existing_locations, known_locs
            )

            # Persist updated story links
            story_data.setdefault('entities', [])
            story_data.setdefault('locations', [])
            for eid in linked_entity_ids:
                if eid not in story_data['entities']:
                    story_data['entities'].append(eid)
            for lid in linked_location_ids:
                if lid not in story_data['locations']:
                    story_data['locations'].append(lid)
            self.storage.save_story(story_data)

            total_chars_found += len(characters)
            total_locs_found += len(locations_found)
            analyzed_results.append({
                'story_id': story_id,
                'story_title': story_title,
                'characters': characters,
                'locations': locations_found,
                'linked_entity_ids': linked_entity_ids,
                'linked_location_ids': linked_location_ids
            })

        # Re-link all stories in the world by shared entities/locations
        all_stories_data = self.storage.list_stories(world_id)
        all_stories = [Story.from_dict(s) for s in all_stories_data]
        linker = StoryLinker()
        linker.link_stories(all_stories, link_by_entities=True, link_by_locations=True, link_by_time=False)

        linked_count = 0
        for story in all_stories:
            if story.linked_stories:
                linked_count += 1
                self.storage.save_story(story.to_dict())

        return {
            'analyzed_stories': analyzed_results,
            'total_characters_found': total_chars_found,
            'total_locations_found': total_locs_found,
            'linked_count': linked_count,
            'message': (
                f'Đã phân tích {total} câu chuyện, tìm thấy {total_chars_found} nhân vật '
                f'và {total_locs_found} địa điểm, liên kết {linked_count} câu chuyện'
            )
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_entities(self, characters, world_id, existing_entities, known_chars):
        """Find or create Entity records for each detected character.

        Args:
            characters: List of dicts with 'name' and 'role' keys from GPT
            world_id: World the entities belong to
            existing_entities: Mutable list of existing entity dicts (updated in place)
            known_chars: Mutable list of known character names (updated in place)

        Returns:
            List of entity_id strings to link to the story
        """
        linked_ids = []
        for char in characters:
            char_name = char.get('name', '')
            char_role = char.get('role', 'nhân vật')
            if not char_name:
                continue

            existing = next(
                (e for e in existing_entities if e.get('name', '').lower() == char_name.lower()),
                None
            )
            if existing:
                entity_id = existing.get('entity_id')
            else:
                new_entity = Entity(name=char_name, entity_type='character', world_id=world_id)
                new_entity.description = char_role
                entity_dict = new_entity.to_dict()
                self.storage.save_entity(entity_dict)
                existing_entities.append(entity_dict)
                entity_id = new_entity.entity_id
                if char_name not in known_chars:
                    known_chars.append(char_name)

            if entity_id not in linked_ids:
                linked_ids.append(entity_id)
        return linked_ids

    def _resolve_locations(self, locations_found, world_id, existing_locations, known_locs):
        """Find or create Location records for each detected location.

        Args:
            locations_found: List of dicts with 'name' and 'description' keys from GPT
            world_id: World the locations belong to
            existing_locations: Mutable list of existing location dicts (updated in place)
            known_locs: Mutable list of known location names (updated in place)

        Returns:
            List of location_id strings to link to the story
        """
        linked_ids = []
        for loc in locations_found:
            loc_name = loc.get('name', '')
            loc_desc = loc.get('description', '')
            if not loc_name:
                continue

            existing = next(
                (l for l in existing_locations if l.get('name', '').lower() == loc_name.lower()),
                None
            )
            if existing:
                location_id = existing.get('location_id')
            else:
                new_location = Location(name=loc_name, world_id=world_id)
                new_location.description = loc_desc
                loc_dict = new_location.to_dict()
                self.storage.save_location(loc_dict)
                existing_locations.append(loc_dict)
                location_id = new_location.location_id
                if loc_name not in known_locs:
                    known_locs.append(loc_name)

            if location_id not in linked_ids:
                linked_ids.append(location_id)
        return linked_ids
