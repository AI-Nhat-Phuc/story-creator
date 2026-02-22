"""Event service for extracting and managing timeline events from stories."""

import hashlib
import json
import logging
import threading
import uuid
from typing import Optional, List, Dict, Any, Callable
from collections import defaultdict

from ai.prompts import PromptTemplates
from core.models import Event

logger = logging.getLogger(__name__)


class EventService:
    """Service for extracting events from stories using GPT and building timelines."""

    def __init__(self, gpt_integration=None, storage=None):
        """
        Initialize EventService.

        Args:
            gpt_integration: GPTIntegration instance (optional, GPT features disabled if None)
            storage: NoSQLStorage instance
        """
        self.gpt = gpt_integration
        self.storage = storage

    def is_available(self) -> bool:
        """Check if GPT is available for event extraction."""
        return self.gpt is not None

    @staticmethod
    def _hash_content(content: str) -> str:
        """Compute SHA-256 hash of story content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def extract_events_from_story(
        self,
        story_id: str,
        force: bool = False,
        callback_success: Optional[Callable] = None,
        callback_error: Optional[Callable] = None
    ) -> None:
        """
        Extract events from a story using GPT (async with threading).

        Flow:
        1. Load story from storage
        2. Compute sha256(content)
        3. Check cache → cache hit + force=False → use cached result
        4. Cache miss or force=True → call GPT → save events + cache

        Args:
            story_id: Story ID to extract events from
            force: If True, bypass cache and re-analyze
            callback_success: Called with result dict on success
            callback_error: Called with exception on failure
        """
        def _extract():
            try:
                # 1. Load story
                story_data = self.storage.load_story(story_id)
                if not story_data:
                    raise ValueError(f"Story not found: {story_id}")

                world_id = story_data.get('world_id', '')
                content = story_data.get('content', '')
                title = story_data.get('title', '')
                genre = story_data.get('metadata', {}).get('genre', '')

                if not content.strip():
                    raise ValueError(f"Story has no content: {story_id}")

                # Build non-empty paragraph index map for validation
                paragraphs = content.split('\n')
                non_empty_indices = [i for i, p in enumerate(paragraphs) if p.strip()]

                # 2. Compute content hash
                content_hash = self._hash_content(content)

                # 3. Check cache (unless force=True)
                if not force:
                    cached = self.storage.get_analysis_cache(story_id, content_hash)
                    if cached:
                        logger.info(f"Using cached analysis for story {story_id}")
                        raw_result = cached['raw_gpt_response']
                        # Rebuild events from cache
                        events = self._process_gpt_result(
                            raw_result, story_id, world_id, title,
                            non_empty_indices=non_empty_indices
                        )
                        if callback_success:
                            callback_success({
                                'story_id': story_id,
                                'events_count': len(events),
                                'from_cache': True,
                                'events': [e.to_dict() for e in events]
                            })
                        return

                # 4. Call GPT
                if not self.gpt:
                    raise RuntimeError("GPT not available for event extraction")

                # Gather world context
                known_characters = self._get_known_characters(world_id)
                known_locations = self._get_known_locations(world_id)
                calendar_info = self._get_calendar_info(world_id)

                # Format content with line numbers so GPT can see exact indices
                content_lines = content[:3000].split('\n')
                numbered_content = '\n'.join(
                    f"{i}| {line}" for i, line in enumerate(content_lines)
                )

                prompt = PromptTemplates.EXTRACT_EVENTS_TEMPLATE.format(
                    story_title=title,
                    story_genre=genre or 'Unknown',
                    story_content_numbered=numbered_content,
                    known_characters=', '.join(known_characters) if known_characters else 'Không có',
                    known_locations=', '.join(known_locations) if known_locations else 'Không có',
                    calendar_info=calendar_info
                )

                response = self.gpt.client.chat.completions.create(
                    model=self.gpt.model,
                    messages=[
                        {"role": "system", "content": PromptTemplates.EXTRACT_EVENTS_SYSTEM},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=1500,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()
                raw_result = json.loads(result_text)

                # 5. Save to cache
                self.storage.save_analysis_cache(
                    story_id, content_hash, raw_result, self.gpt.model
                )

                # 6. Delete old events for this story and save new ones
                self.storage.delete_events_by_story(story_id)

                # Build non-empty paragraph indices for validation
                paragraphs = content.split('\n')
                non_empty_indices = [i for i, p in enumerate(paragraphs) if p.strip()]

                events = self._process_gpt_result(
                    raw_result, story_id, world_id, title,
                    non_empty_indices=non_empty_indices
                )

                if callback_success:
                    callback_success({
                        'story_id': story_id,
                        'events_count': len(events),
                        'from_cache': False,
                        'events': [e.to_dict() for e in events]
                    })

            except Exception as e:
                logger.error(f"Error extracting events from story {story_id}: {e}")
                if callback_error:
                    callback_error(e)

        thread = threading.Thread(target=_extract, daemon=True)
        thread.start()

    def extract_events_from_world(
        self,
        world_id: str,
        force: bool = False,
        callback_success: Optional[Callable] = None,
        callback_error: Optional[Callable] = None
    ) -> None:
        """
        Extract events from ALL stories in a world using a SINGLE GPT prompt.
        Combines all stories into one mega-prompt for analysis.

        Args:
            world_id: World ID to extract events from
            force: If True, bypass cache and re-analyze
            callback_success: Called with result dict on success
            callback_error: Called with exception on failure
        """
        def _extract():
            try:
                # 1. Load all stories in this world
                stories = self.storage.list_stories(world_id)
                if not stories:
                    raise ValueError(f"No stories found in world: {world_id}")

                # 2. Build combined content with story separators
                combined_content_parts = []
                story_metadata_list = []
                story_map = {}  # story_index → story_id, content lines, non_empty_indices

                for story_idx, story_data in enumerate(stories):
                    story_id = story_data.get('story_id', '')
                    title = story_data.get('title', f'Story {story_idx + 1}')
                    genre = story_data.get('metadata', {}).get('genre', 'Unknown')
                    content = story_data.get('content', '')

                    if not content.strip():
                        continue

                    paragraphs = content.split('\n')
                    non_empty_indices = [i for i, p in enumerate(paragraphs) if p.strip()]

                    # Add separator header
                    combined_content_parts.append(f"=== STORY_{story_idx}: {title} ({genre}) ===")

                    # Add numbered lines
                    content_lines = content[:3000].split('\n')
                    for line_idx, line in enumerate(content_lines):
                        combined_content_parts.append(f"{line_idx}| {line}")

                    story_metadata_list.append({
                        'story_index': story_idx,
                        'story_id': story_id,
                        'title': title,
                        'genre': genre
                    })

                    story_map[story_idx] = {
                        'story_id': story_id,
                        'title': title,
                        'non_empty_indices': non_empty_indices
                    }

                combined_content = '\n'.join(combined_content_parts)

                # 3. Compute hash of combined content
                content_hash = self._hash_content(combined_content)
                cache_key = f"world_{world_id}"

                # 4. Check cache (unless force=True)
                if not force:
                    cached = self.storage.get_analysis_cache(cache_key, content_hash)
                    if cached:
                        logger.info(f"Using cached analysis for world {world_id}")
                        raw_result = cached['raw_gpt_response']
                        # Process combined result
                        all_events = self._process_combined_gpt_result(
                            raw_result, story_map, world_id
                        )
                        if callback_success:
                            callback_success({
                                'world_id': world_id,
                                'total_events': len(all_events),
                                'from_cache': True,
                                'events': [e.to_dict() for e in all_events]
                            })
                        return

                # 5. Call GPT with combined content
                if not self.gpt:
                    raise RuntimeError("GPT not available for event extraction")

                # Gather world context
                known_characters = self._get_known_characters(world_id)
                known_locations = self._get_known_locations(world_id)
                calendar_info = self._get_calendar_info(world_id)

                # Build story list for prompt
                story_list = '\n'.join([
                    f"- STORY_{m['story_index']}: {m['title']} ({m['genre']})"
                    for m in story_metadata_list
                ])

                prompt = f"""Bạn là một nhà phân tích văn học chuyên nghiệp. Nhiệm vụ: trích xuất các SỰ KIỆN quan trọng từ TẤT CẢ các câu chuyện sau đây trong cùng một thế giới.

DANH SÁCH CÁC CÂU CHUYỆN:
{story_list}

NỘI DUNG CÁC CÂU CHUYỆN (có đánh số dòng):
{combined_content}

NGUYÊN TẮC:
1. Mỗi sự kiện PHẢI gắn với STORY_INDEX (0, 1, 2, ...) của câu chuyện chứa nó
2. story_position là SỐ THỨ TỰ ĐẦU DÒNG (số trước dấu |) trong câu chuyện đó
3. Chỉ trích xuất sự kiện từ đoạn văn CÓ NỘI DUNG (không phải dòng trống)
4. Tạo connections giữa các sự kiện TRONG và GIỮA các câu chuyện
5. Không tạo sự kiện với vị trí đoạn văn trống

NHÂN VẬT BIẾT: {', '.join(known_characters) if known_characters else 'Không có'}
ĐỊA ĐIỂM BIẾT: {', '.join(known_locations) if known_locations else 'Không có'}
LỊCH: {calendar_info}

Trả về JSON với format:
{{
  "events": [
    {{
      "story_index": 0,
      "title": "Tên sự kiện",
      "description": "Mô tả",
      "year": 1200,
      "era": "Kỷ nguyên ABC",
      "characters": ["Tên nhân vật"],
      "locations": ["Tên địa điểm"],
      "story_position": 5,
      "abstract_image_seed": "mô tả hình ảnh trừu tượng"
    }}
  ],
  "connections": [
    {{
      "from_event_index": 0,
      "to_event_index": 1,
      "relation_type": "causal",
      "relation_label": "Dẫn đến"
    }}
  ]
}}"""

                response = self.gpt.client.chat.completions.create(
                    model=self.gpt.model,
                    messages=[
                        {"role": "system", "content": "Bạn là trợ lý phân tích sự kiện chuyên nghiệp. Luôn trả về JSON hợp lệ."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=4000,  # Increased for multiple stories
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()
                raw_result = json.loads(result_text)

                # 6. Save to cache
                self.storage.save_analysis_cache(
                    cache_key, content_hash, raw_result, self.gpt.model
                )

                # 7. Delete old events for ALL stories in this world
                for story in stories:
                    self.storage.delete_events_by_story(story.get('story_id'))

                # 8. Process combined result
                all_events = self._process_combined_gpt_result(
                    raw_result, story_map, world_id
                )

                if callback_success:
                    callback_success({
                        'world_id': world_id,
                        'total_events': len(all_events),
                        'from_cache': False,
                        'events': [e.to_dict() for e in all_events]
                    })

            except Exception as e:
                logger.error(f"Error extracting events from world {world_id}: {e}")
                if callback_error:
                    callback_error(e)

        thread = threading.Thread(target=_extract, daemon=True)
        thread.start()

    def _process_combined_gpt_result(
        self,
        raw_result: Dict[str, Any],
        story_map: Dict[int, Dict[str, Any]],
        world_id: str
    ) -> List[Event]:
        """Process GPT result from combined world analysis.

        Args:
            raw_result: Raw JSON from GPT (with story_index in each event)
            story_map: {story_index → {story_id, title, non_empty_indices}}
            world_id: World ID

        Returns:
            List of Event objects
        """
        events_data = raw_result.get('events', [])
        connections_data = raw_result.get('connections', [])

        # Resolve character/location names to IDs
        char_name_to_id = self._build_character_name_map(world_id)
        loc_name_to_id = self._build_location_name_map(world_id)

        created_events = []
        event_id_map = {}  # GPT event index → Event object

        for i, evt in enumerate(events_data):
            story_idx = evt.get('story_index', 0)

            # Get story info
            if story_idx not in story_map:
                logger.warning(f"Event {i} references invalid story_index {story_idx}")
                continue

            story_info = story_map[story_idx]
            story_id = story_info['story_id']
            story_title = story_info['title']
            non_empty_indices = story_info['non_empty_indices']

            # Resolve character names to IDs
            char_ids = []
            for name in evt.get('characters', []):
                eid = char_name_to_id.get(name.lower())
                if eid:
                    char_ids.append(eid)

            # Resolve location names to IDs
            loc_ids = []
            for name in evt.get('locations', []):
                lid = loc_name_to_id.get(name.lower())
                if lid:
                    loc_ids.append(lid)

            # Validate story_position
            gpt_pos = evt.get('story_position', 0)
            raw_pos = gpt_pos
            if non_empty_indices and raw_pos not in non_empty_indices:
                raw_pos = min(non_empty_indices, key=lambda x: abs(x - raw_pos))
                logger.info(f"Event '{evt.get('title', '')}': GPT pos {gpt_pos} → snapped to {raw_pos}")

            # Skip empty events
            if not evt.get('title', '').strip() and not evt.get('description', '').strip():
                logger.warning(f"Skipping empty event at index {i}")
                continue

            event = Event(
                title=evt.get('title', f'Sự kiện {i+1}'),
                description=evt.get('description', ''),
                story_id=story_id,
                world_id=world_id,
                year=evt.get('year', 0),
                era=evt.get('era', ''),
                characters=char_ids,
                locations=loc_ids,
                story_position=raw_pos,
                metadata={
                    'abstract_image_seed': evt.get('abstract_image_seed', ''),
                    'character_names': evt.get('characters', []),
                    'location_names': evt.get('locations', []),
                    'story_title': story_title
                }
            )

            event_id_map[i] = event
            created_events.append(event)

        # Process connections
        for conn in connections_data:
            from_idx = conn.get('from_event_index', 0)
            to_idx = conn.get('to_event_index', 0)

            if from_idx in event_id_map and to_idx in event_id_map:
                from_event = event_id_map[from_idx]
                to_event = event_id_map[to_idx]

                from_event.add_connection(
                    target_event_id=to_event.event_id,
                    relation_type=conn.get('relation_type', 'temporal'),
                    relation_label=conn.get('relation_label', '')
                )

        # Save all events
        for event in created_events:
            self.storage.save_event(event.to_dict())

        return created_events

    def _process_gpt_result(
        self,
        raw_result: Dict[str, Any],
        story_id: str,
        world_id: str,
        story_title: str,
        non_empty_indices: Optional[List[int]] = None
    ) -> List[Event]:
        """Process raw GPT result into Event objects and save to storage.

        Args:
            raw_result: Raw JSON from GPT
            story_id: Story ID
            world_id: World ID
            story_title: Story title for context
            non_empty_indices: List of paragraph indices that have actual content

        Returns:
            List of Event objects
        """
        events_data = raw_result.get('events', [])
        connections_data = raw_result.get('connections', [])

        # Resolve character names to entity IDs
        char_name_to_id = self._build_character_name_map(world_id)
        loc_name_to_id = self._build_location_name_map(world_id)

        created_events = []
        event_id_map = {}  # index → event_id mapping for connections

        for i, evt in enumerate(events_data):
            # Resolve character names to IDs
            char_ids = []
            for name in evt.get('characters', []):
                eid = char_name_to_id.get(name.lower())
                if eid:
                    char_ids.append(eid)

            # Resolve location names to IDs
            loc_ids = []
            for name in evt.get('locations', []):
                lid = loc_name_to_id.get(name.lower())
                if lid:
                    loc_ids.append(lid)

            # Validate story_position points to non-empty paragraph
            gpt_pos = evt.get('story_position', i)
            raw_pos = gpt_pos
            if non_empty_indices is not None and non_empty_indices:
                # If position points to an empty line, snap to nearest non-empty
                if raw_pos not in non_empty_indices:
                    raw_pos = min(non_empty_indices, key=lambda x: abs(x - raw_pos))
                    logger.info(f"Event '{evt.get('title', '')}': GPT pos {gpt_pos} → snapped to {raw_pos}")
            logger.info(f"Event '{evt.get('title', '')}': final story_position={raw_pos} (GPT returned {gpt_pos})")

            # Skip events with empty title/description (GPT hallucinations)
            if not evt.get('title', '').strip() and not evt.get('description', '').strip():
                logger.warning(f"Skipping empty event at index {i} for story {story_id}")
                continue

            event = Event(
                title=evt.get('title', f'Sự kiện {i+1}'),
                description=evt.get('description', ''),
                story_id=story_id,
                world_id=world_id,
                year=evt.get('year', 0),
                era=evt.get('era', ''),
                characters=char_ids,
                locations=loc_ids,
                story_position=raw_pos,
                metadata={
                    'abstract_image_seed': evt.get('abstract_image_seed', ''),
                    'character_names': evt.get('characters', []),
                    'location_names': evt.get('locations', [])
                }
            )

            event_id_map[i] = event.event_id
            created_events.append(event)

        # Process connections
        for conn in connections_data:
            from_idx = conn.get('from_event_index', 0)
            to_idx = conn.get('to_event_index', 0)
            if from_idx < len(created_events) and to_idx < len(created_events):
                created_events[from_idx].add_connection(
                    target_event_id=event_id_map[to_idx],
                    relation_type=conn.get('relation_type', 'temporal'),
                    relation_label=conn.get('relation_label', '')
                )

        # Save all events
        for event in created_events:
            self.storage.save_event(event.to_dict())

        return created_events

    def _get_known_characters(self, world_id: str) -> List[str]:
        """Get character names for a world."""
        entities = self.storage.list_entities(world_id)
        return [e.get('name', '') for e in entities if e.get('name')]

    def _get_known_locations(self, world_id: str) -> List[str]:
        """Get location names for a world."""
        locations = self.storage.list_locations(world_id)
        return [l.get('name', '') for l in locations if l.get('name')]

    def _get_calendar_info(self, world_id: str) -> str:
        """Get calendar info string for a world."""
        world_data = self.storage.load_world(world_id)
        if not world_data:
            return "Không có thông tin lịch"
        calendar = world_data.get('metadata', {}).get('calendar', {})
        if not calendar:
            return "Không có thông tin lịch"
        return (
            f"Era: {calendar.get('current_era', 'N/A')}, "
            f"Current year: {calendar.get('current_year', 'N/A')}, "
            f"Year name: {calendar.get('year_name', 'Năm')}"
        )

    def _build_character_name_map(self, world_id: str) -> Dict[str, str]:
        """Build a lowercase name → entity_id map for a world."""
        entities = self.storage.list_entities(world_id)
        return {e.get('name', '').lower(): e.get('entity_id', '') for e in entities if e.get('name')}

    def _build_location_name_map(self, world_id: str) -> Dict[str, str]:
        """Build a lowercase name → location_id map for a world."""
        locations = self.storage.list_locations(world_id)
        return {l.get('name', '').lower(): l.get('location_id', '') for l in locations if l.get('name')}

    def get_world_events(self, world_id: str) -> List[Dict[str, Any]]:
        """Get all events for a world."""
        return self.storage.list_events_by_world(world_id)

    def get_cross_story_connections(self, world_id: str) -> List[Dict[str, Any]]:
        """Find connections between events from different stories
        based on shared characters/locations.

        Excludes world-level locations (the world itself) from connection reasons.

        Returns:
            List of connection dicts: [{from_event_id, to_event_id, relation_type, relation_label}]
        """
        events = self.storage.list_events_by_world(world_id)
        if len(events) < 2:
            return []

        # Get world name to exclude it as a location connection reason
        world_data = self.storage.load_world(world_id)
        world_name = (world_data.get('name', '') if world_data else '').lower()

        cross_connections = []

        # Build inverted indices: character_id → [event dicts], location_id → [event dicts]
        char_to_events = defaultdict(list)
        loc_to_events = defaultdict(list)

        for evt in events:
            for cid in evt.get('characters', []):
                char_to_events[cid].append(evt)
            for lid in evt.get('locations', []):
                loc_to_events[lid].append(evt)

        seen_pairs = set()

        # Character-based connections
        for cid, evts in char_to_events.items():
            # Only cross-story connections
            for i in range(len(evts)):
                for j in range(i + 1, len(evts)):
                    if evts[i]['story_id'] != evts[j]['story_id']:
                        pair = tuple(sorted([evts[i]['event_id'], evts[j]['event_id']]))
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            # Get character name
                            entity = self.storage.load_entity(cid)
                            char_name = entity.get('name', 'Unknown') if entity else 'Unknown'
                            cross_connections.append({
                                'from_event_id': pair[0],
                                'to_event_id': pair[1],
                                'relation_type': 'character',
                                'relation_label': f'Nhân vật chung: {char_name}'
                            })

        # Location-based connections (skip world-level locations)
        for lid, evts in loc_to_events.items():
            # Resolve location name and skip if it matches the world name
            location = self.storage.load_location(lid)
            loc_name = location.get('name', 'Unknown') if location else 'Unknown'
            if loc_name.lower() == world_name or loc_name.lower().strip() == world_name.strip():
                continue

            for i in range(len(evts)):
                for j in range(i + 1, len(evts)):
                    if evts[i]['story_id'] != evts[j]['story_id']:
                        pair = tuple(sorted([evts[i]['event_id'], evts[j]['event_id']]))
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            cross_connections.append({
                                'from_event_id': pair[0],
                                'to_event_id': pair[1],
                                'relation_type': 'location',
                                'relation_label': f'Địa điểm chung: {loc_name}'
                            })

        return cross_connections

    def build_timeline(self, world_id: str) -> Dict[str, Any]:
        """Build timeline data structure for frontend.

        Returns:
            {
                world_id: str,
                world_name: str,
                timeline: {
                    years: [{year, era, events: [...]}],
                    connections: [...]
                }
            }
        """
        world_data = self.storage.load_world(world_id)
        if not world_data:
            return {'world_id': world_id, 'world_name': 'Unknown', 'timeline': {'years': [], 'connections': []}}

        events = self.storage.list_events_by_world(world_id)

        # Group events by year
        year_groups = defaultdict(list)
        for evt in events:
            year = evt.get('year', 0)
            # Enrich with story title
            story_data = self.storage.load_story(evt.get('story_id', ''))
            evt['story_title'] = story_data.get('title', 'Unknown') if story_data else 'Unknown'

            # Enrich character/location names
            evt['character_details'] = []
            for cid in evt.get('characters', []):
                entity = self.storage.load_entity(cid)
                if entity:
                    evt['character_details'].append({
                        'entity_id': cid,
                        'name': entity.get('name', 'Unknown')
                    })

            evt['location_details'] = []
            for lid in evt.get('locations', []):
                location = self.storage.load_location(lid)
                if location:
                    evt['location_details'].append({
                        'location_id': lid,
                        'name': location.get('name', 'Unknown')
                    })

            year_groups[year].append(evt)

        # Sort years and build timeline
        sorted_years = sorted(year_groups.keys())
        years_list = []
        for year in sorted_years:
            year_events = sorted(year_groups[year], key=lambda e: e.get('story_position', 0))
            # Get era from first event that has one
            era = ''
            for evt in year_events:
                if evt.get('era'):
                    era = evt['era']
                    break
            years_list.append({
                'year': year,
                'era': era,
                'events': year_events
            })

        # Gather all connections (intra-story + cross-story)
        all_connections = []

        # Intra-story connections (already in event.connections)
        for evt in events:
            for conn in evt.get('connections', []):
                all_connections.append({
                    'from_event_id': evt['event_id'],
                    'to_event_id': conn.get('target_event_id'),
                    'relation_type': conn.get('relation_type', 'temporal'),
                    'relation_label': conn.get('relation_label', '')
                })

        # Cross-story connections
        cross_conns = self.get_cross_story_connections(world_id)
        all_connections.extend(cross_conns)

        return {
            'world_id': world_id,
            'world_name': world_data.get('name', 'Unknown'),
            'timeline': {
                'years': years_list,
                'connections': all_connections
            }
        }

    def clear_story_cache(self, story_id: str) -> bool:
        """Clear the analysis cache for a story."""
        return self.storage.delete_analysis_cache(story_id)
