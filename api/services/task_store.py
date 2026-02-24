"""Database-backed GPT task store.

Replaces the in-memory gpt_results dict with persistent storage,
so tasks survive Vercel cold starts and page refreshes.

Implements dict-like interface for backward compatibility with
existing gpt_routes.py and event_routes.py code that does:
    gpt_results[task_id] = {'status': 'pending'}
    result = gpt_results.get(task_id)
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class TaskStore:
    """Dict-like wrapper that persists GPT task results in the database.

    Usage (drop-in replacement for dict):
        store = TaskStore(storage)
        store[task_id] = {'status': 'pending'}      # save
        result = store.get(task_id)                  # load
        result = store[task_id]                      # load (KeyError if missing)
    """

    def __init__(self, storage):
        self.storage = storage

    def __setitem__(self, task_id: str, value: dict):
        """Save or update a task result."""
        now = datetime.now(timezone.utc).isoformat()
        task_data = {
            'task_id': task_id,
            **value,
            'updated_at': now
        }
        # Only set created_at on first write
        existing = self.storage.load_gpt_task(task_id)
        if existing:
            task_data['created_at'] = existing.get('created_at', now)
            self.storage.update_gpt_task(task_id, task_data)
        else:
            task_data['created_at'] = now
            self.storage.save_gpt_task(task_data)

    def __getitem__(self, task_id: str) -> dict:
        """Load a task result. Raises KeyError if not found."""
        result = self.storage.load_gpt_task(task_id)
        if result is None:
            raise KeyError(task_id)
        return result

    def get(self, task_id: str, default=None):
        """Load a task result, returning default if not found."""
        result = self.storage.load_gpt_task(task_id)
        return result if result is not None else default

    def __contains__(self, task_id: str) -> bool:
        return self.storage.load_gpt_task(task_id) is not None

    def cleanup(self, max_age_hours: int = 24) -> int:
        """Remove old tasks. Call periodically to prevent unbounded growth."""
        return self.storage.cleanup_old_gpt_tasks(max_age_hours)
