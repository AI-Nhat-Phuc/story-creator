"""Invitation model for co-author collaboration requests."""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class Invitation:
    """Represents a co-author invitation for a world."""

    def __init__(
        self,
        world_id: str,
        invited_by: str,
        invitee_id: str,
        invitation_id: Optional[str] = None,
        status: str = 'pending',
        created_at: Optional[str] = None
    ):
        self.invitation_id = invitation_id or str(uuid.uuid4())
        self.world_id = world_id
        self.invited_by = invited_by
        self.invitee_id = invitee_id
        self.status = status  # pending | accepted | declined
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "invitation",
            "invitation_id": self.invitation_id,
            "world_id": self.world_id,
            "invited_by": self.invited_by,
            "invitee_id": self.invitee_id,
            "status": self.status,
            "created_at": self.created_at
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invitation':
        return cls(
            world_id=data["world_id"],
            invited_by=data["invited_by"],
            invitee_id=data["invitee_id"],
            invitation_id=data.get("invitation_id"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at")
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Invitation':
        return cls.from_dict(json.loads(json_str))
