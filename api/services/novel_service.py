"""Novel service — ordering, neighbors, and paginated content for world novels.

Spec clauses:
  BR-1,2 — ordered by (order ASC, created_at ASC)
  BR-5   — if total lines ≤ line_budget, chapters returned fully
  BR-6,8 — if > line_budget, split mid-chapter; each batch ≤ line_budget
  BR-15  — assign_next_order = max(order)+1 across stories in a world
"""

import base64
import json
from typing import Any, Dict, List, Optional


def _sort_key(story: Dict[str, Any]):
    """Sort by (order ASC, created_at ASC). Stories with no `order` go last."""
    order = story.get('order')
    if order is None:
        order = float('inf')
    return (order, story.get('created_at') or '')


def _ordered_stories(storage, world_id: str, user_id: Optional[str]) -> List[Dict[str, Any]]:
    stories = storage.list_stories(world_id=world_id, user_id=user_id)
    return sorted(stories, key=_sort_key)


def _encode_cursor(story_id: str, line: int) -> str:
    # Cursor is anchored by story_id (always unique) rather than `order`
    # because legacy stories may share order=None.
    payload = json.dumps({'story_id': story_id, 'line': line}).encode('utf-8')
    return base64.urlsafe_b64encode(payload).decode('ascii').rstrip('=')


def _decode_cursor(cursor: str) -> Dict[str, Any]:
    padded = cursor + '=' * (-len(cursor) % 4)
    payload = base64.urlsafe_b64decode(padded.encode('ascii'))
    return json.loads(payload.decode('utf-8'))


def _split_lines(content: str) -> List[str]:
    if not content:
        return []
    return content.split('\n')


class NovelService:
    """Stateless helpers for novel ordering and content pagination."""

    @staticmethod
    def get_ordered_stories(storage, world_id: str,
                            user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return _ordered_stories(storage, world_id, user_id)

    @staticmethod
    def assign_next_order(storage, world_id: str,
                          user_id: Optional[str] = None) -> int:
        # Use raw collection to see ALL stories in the world regardless of
        # permissions — order must be unique within a world.
        if hasattr(storage, 'stories'):
            docs = list(storage.stories.find({'world_id': world_id}))
        else:
            docs = storage.list_stories(world_id=world_id, user_id=user_id)
        orders = [d.get('order') for d in docs if d.get('order') is not None]
        return (max(orders) + 1) if orders else 1

    @staticmethod
    def get_neighbors(storage, world_id: str, story_id: str,
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        ordered = _ordered_stories(storage, world_id, user_id)
        prev_story = None
        next_story = None
        for idx, s in enumerate(ordered):
            if s.get('story_id') == story_id:
                if idx > 0:
                    prev_story = ordered[idx - 1]
                if idx < len(ordered) - 1:
                    next_story = ordered[idx + 1]
                break

        def _summary(s):
            if not s:
                return None
            return {
                'story_id': s.get('story_id'),
                'title': s.get('title'),
                'order': s.get('order'),
            }

        return {'prev': _summary(prev_story), 'next': _summary(next_story)}

    @staticmethod
    def get_content_batch(storage, world_id: str,
                          cursor: Optional[str] = None,
                          line_budget: int = 100,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """Return a batch of chapter blocks up to `line_budget` lines total.

        - Without cursor: start from the first chapter.
        - With cursor: resume from {order, line}.
        - If a chapter's remaining lines exceed the remaining budget, split
          mid-chapter and emit a cursor pointing at the next line.
        """
        ordered = _ordered_stories(storage, world_id, user_id)

        start_story_id: Optional[str] = None
        start_line = 0
        if cursor:
            decoded = _decode_cursor(cursor)
            start_story_id = decoded.get('story_id')
            start_line = decoded.get('line', 0)

        start_idx = 0
        if start_story_id is not None:
            matched = False
            for i, s in enumerate(ordered):
                if s.get('story_id') == start_story_id:
                    start_idx = i
                    matched = True
                    break
            if not matched:
                return {'blocks': [], 'has_more': False, 'next_cursor': None}

        blocks: List[Dict[str, Any]] = []
        remaining = line_budget
        next_cursor: Optional[str] = None
        has_more = False

        idx = start_idx
        while idx < len(ordered):
            if remaining <= 0:
                has_more = True
                s = ordered[idx]
                next_cursor = _encode_cursor(s.get('story_id'), 0)
                break

            s = ordered[idx]
            content = s.get('content') or ''
            all_lines = _split_lines(content)
            total_lines = len(all_lines)

            begin = start_line if idx == start_idx else 0
            if begin > total_lines:
                begin = total_lines

            available = total_lines - begin
            take = min(available, remaining)
            end = begin + take
            is_complete = (end >= total_lines)

            chunk_content = '\n'.join(all_lines[begin:end])
            blocks.append({
                'story_id': s.get('story_id'),
                'title': s.get('title'),
                'order': s.get('order'),
                'chapter_number': s.get('chapter_number'),
                'content': chunk_content,
                'start_line': begin,
                'end_line': end,
                'total_lines': total_lines,
                'is_complete': is_complete,
            })
            remaining -= take

            if not is_complete:
                has_more = True
                next_cursor = _encode_cursor(s.get('story_id'), end)
                break

            idx += 1

        return {
            'blocks': blocks,
            'has_more': has_more,
            'next_cursor': next_cursor,
        }
