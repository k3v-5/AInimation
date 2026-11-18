"""Serialization, canonical JSON encoding, and schema validation for bridge messages."""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Union
from uaf.bridge.ue5.protocol.messages import BridgeMessage, BridgeMessageType, UpdatePriority


class BridgeSchemaValidationError(Exception):
    """Raised when a message payload violates structural contracts."""
    pass


class BridgeMessageCodec:
    """Encodes and decodes BridgeMessage instances with strict schema validation."""

    MAX_PAYLOAD_SIZE_BYTES = 16 * 1024 * 1024  # 16 MB

    @staticmethod
    def encode(message: BridgeMessage, as_bytes: bool = True) -> Union[bytes, str]:
        data = message.to_dict()
        serialized = json.dumps(data, sort_keys=True)
        encoded_bytes = serialized.encode("utf-8")
        if len(encoded_bytes) > BridgeMessageCodec.MAX_PAYLOAD_SIZE_BYTES:
            raise BridgeSchemaValidationError(
                f"Message {message.message_id} exceeds max payload size ({len(encoded_bytes)} bytes)"
            )
        return encoded_bytes if as_bytes else serialized

    @staticmethod
    def decode(raw_payload: Union[str, bytes]) -> BridgeMessage:
        if isinstance(raw_payload, bytes):
            if len(raw_payload) > BridgeMessageCodec.MAX_PAYLOAD_SIZE_BYTES:
                raise BridgeSchemaValidationError("Raw payload exceeds max payload size limit")
            try:
                raw_json = raw_payload.decode("utf-8")
            except Exception as e:
                raise BridgeSchemaValidationError(f"Invalid UTF-8 in bridge message: {e}") from e
        else:
            raw_json = raw_payload
            if len(raw_json.encode("utf-8")) > BridgeMessageCodec.MAX_PAYLOAD_SIZE_BYTES:
                raise BridgeSchemaValidationError("Raw payload exceeds max payload size limit")

        try:
            data = json.loads(raw_json)
        except Exception as e:
            raise BridgeSchemaValidationError(f"Invalid JSON in bridge message: {e}") from e

        if not isinstance(data, dict):
            raise BridgeSchemaValidationError("Decoded payload must be a JSON object")

        for req in ("message_type", "message_id"):
            if req not in data:
                raise BridgeSchemaValidationError(f"Missing required envelope field '{req}'")

        try:
            msg_type = BridgeMessageType(data["message_type"])
        except ValueError:
            raise BridgeSchemaValidationError(f"Unknown message type '{data['message_type']}'")

        priority_str = data.get("priority", "NORMAL")
        try:
            priority = UpdatePriority(priority_str)
        except ValueError:
            priority = UpdatePriority.NORMAL

        return BridgeMessage(
            message_type=msg_type,
            payload=data.get("payload", {}),
            message_id=data["message_id"],
            sender_id=data.get("sender_id", ""),
            session_id=data.get("session_id", ""),
            timestamp_ns=data.get("timestamp_ns", 0),
            priority=priority,
            requires_ack=data.get("requires_ack", False),
            ack_message_id=data.get("ack_message_id"),
        )
