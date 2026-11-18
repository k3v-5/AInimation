"""
UAF-81.95: Co-Pilot Protocol Message Builders & Serialization.
JSON-RPC formatters, message factory methods, and round-trip verification.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from uaf.copilot.core.contracts import (
    CoPilotCommandType,
    CoPilotMessage,
    LiveActorSync,
    TerrainRegionPatch,
    Transform3D,
)


def serialize_message(message: CoPilotMessage) -> str:
    """Serializes a CoPilotMessage into a compact JSON string."""
    return message.model_dump_json()


def deserialize_message(raw_json: str) -> CoPilotMessage:
    """Deserializes raw JSON into a validated CoPilotMessage."""
    data = json.loads(raw_json)
    return CoPilotMessage(**data)


class MessageBuilder:
    """Factory methods for constructing strictly typed co-pilot synchronization messages."""

    @staticmethod
    def build_handshake(
        sender: str = "AOE_CORE",
        api_version: str = "81.95.0",
        capabilities: Optional[List[str]] = None,
    ) -> CoPilotMessage:
        caps = capabilities or ["terrain_sync", "wfc_sync", "spawner_sync", "audio_sync", "designer_lock"]
        return CoPilotMessage(
            command_type=CoPilotCommandType.HANDSHAKE,
            sender=sender,
            timestamp=time.time(),
            payload={
                "api_version": api_version,
                "capabilities": caps,
                "status": "READY",
            },
        )

    @staticmethod
    def build_ping(sender: str = "AOE_CORE") -> CoPilotMessage:
        return CoPilotMessage(
            command_type=CoPilotCommandType.PING,
            sender=sender,
            timestamp=time.time(),
            payload={},
        )

    @staticmethod
    def build_pong(reply_to_id: str, sender: str = "UE5_EDITOR") -> CoPilotMessage:
        return CoPilotMessage(
            command_type=CoPilotCommandType.PONG,
            sender=sender,
            timestamp=time.time(),
            payload={"reply_to_id": reply_to_id},
        )

    @staticmethod
    def build_terrain_sync(
        patch: TerrainRegionPatch,
        sender: str = "AOE_CORE",
    ) -> CoPilotMessage:
        return CoPilotMessage(
            command_type=CoPilotCommandType.SYNC_TERRAIN_REGION,
            sender=sender,
            timestamp=time.time(),
            payload=patch.model_dump(),
        )

    @staticmethod
    def build_actor_sync(
        actors: List[LiveActorSync],
        sender: str = "AOE_CORE",
    ) -> CoPilotMessage:
        return CoPilotMessage(
            command_type=CoPilotCommandType.SYNC_SPAWNER_AI,
            sender=sender,
            timestamp=time.time(),
            payload={"actors": [a.model_dump() for a in actors]},
        )

    @staticmethod
    def build_feedback_transform(
        actor_id: str,
        new_transform: Transform3D,
        lock_designer: bool = True,
        sender: str = "UE5_EDITOR",
    ) -> CoPilotMessage:
        return CoPilotMessage(
            command_type=CoPilotCommandType.FEEDBACK_TRANSFORM_CHANGED,
            sender=sender,
            timestamp=time.time(),
            payload={
                "actor_id": actor_id,
                "transform": new_transform.model_dump(),
                "lock_designer": lock_designer,
            },
        )

    @staticmethod
    def build_ack(
        reply_to_id: str,
        sender: str = "AOE_CORE",
        details: Optional[Dict[str, Any]] = None,
    ) -> CoPilotMessage:
        payload = {"reply_to_id": reply_to_id, "status": "ACK"}
        if details:
            payload.update(details)
        return CoPilotMessage(
            command_type=CoPilotCommandType.ACK,
            sender=sender,
            timestamp=time.time(),
            payload=payload,
        )

    @staticmethod
    def build_error(
        reply_to_id: str,
        error_message: str,
        error_code: int = 500,
        sender: str = "AOE_CORE",
    ) -> CoPilotMessage:
        return CoPilotMessage(
            command_type=CoPilotCommandType.ERROR,
            sender=sender,
            timestamp=time.time(),
            payload={
                "reply_to_id": reply_to_id,
                "error": error_message,
                "code": error_code,
            },
        )
