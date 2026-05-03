"""In-memory activity log service (mock layer).

Replace the _store list with DB-backed reads/writes to move to persistent storage.
The public interface (log / get_user_logs / get_all_logs) stays the same.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class ActivityLogService:
    """Thread-safe in-memory store for user activity events."""

    VALID_ACTIONS = frozenset({
        'create_story',
        'update_story',
        'delete_story',
    })

    def __init__(self) -> None:
        self._store: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def log(
        self,
        user_id: str,
        action: str,
        resource_type: str = 'story',
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record an activity and return the log entry."""
        entry: Dict[str, Any] = {
            'log_id': str(uuid.uuid4()),
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'metadata': metadata or {},
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._store.append(entry)
        return entry

    def get_user_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent logs for a specific user, newest-first."""
        with self._lock:
            logs = [e for e in self._store if e['user_id'] == user_id]
        return sorted(logs, key=lambda e: e['timestamp'], reverse=True)[:limit]

    def get_all_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Return all logs newest-first."""
        with self._lock:
            logs = list(self._store)
        return sorted(logs, key=lambda e: e['timestamp'], reverse=True)[:limit]


# ── Singleton ────────────────────────────────────────────────────────────────

_service: Optional[ActivityLogService] = None


def init_activity_log_service() -> ActivityLogService:
    """Create and store the singleton; call once at startup."""
    global _service
    if _service is None:
        _service = ActivityLogService()
    return _service


def get_activity_log_service() -> Optional[ActivityLogService]:
    """Return the singleton (None before init_activity_log_service is called)."""
    return _service
