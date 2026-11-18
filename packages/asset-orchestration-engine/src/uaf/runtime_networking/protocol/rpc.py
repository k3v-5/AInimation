"""
UAF-81.83: Remote Procedure Call (RPC) Dispatcher, Authority Enforcement & Idempotency.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional, Set

from ..models.definition import (
    AuthorityType,
    InvalidAuthorityError,
    NetworkEntityId,
    RPCMessage,
    RPCType,
)


class RPCDispatcher:
    """
    Manages registration, authority validation, idempotency caching,
    and invocation of Remote Procedure Calls.
    """

    def __init__(self, max_idempotency_cache: int = 10000):
        self._handlers: Dict[str, Callable[[RPCMessage, Any], Any]] = {}
        self._handler_authorities: Dict[str, AuthorityType] = {}
        self._idempotency_cache: Dict[str, Any] = {}
        self._cached_order: list[str] = []
        self._max_cache_size = max_idempotency_cache

    def register_handler(
        self,
        rpc_name: str,
        handler: Callable[[RPCMessage, Any], Any],
        required_authority: AuthorityType = AuthorityType.SERVER_AUTHORITY,
    ) -> None:
        """Register a callback handler for an RPC name."""
        self._handlers[rpc_name] = handler
        self._handler_authorities[rpc_name] = required_authority

    def has_handler(self, rpc_name: str) -> bool:
        """Check if an RPC handler is registered."""
        return rpc_name in self._handlers

    def dispatch(
        self,
        message: RPCMessage,
        caller_authority: AuthorityType = AuthorityType.SERVER_AUTHORITY,
        context: Any = None,
    ) -> Any:
        """
        Validate authority, verify idempotency, and execute the RPC handler.
        Raises InvalidAuthorityError if caller lacks required authority.
        """
        # Idempotency check for repeated reliable operations
        if message.operation_id in self._idempotency_cache:
            return self._idempotency_cache[message.operation_id]

        rpc_name = message.rpc_name
        if rpc_name not in self._handlers:
            raise KeyError(f"No RPC handler registered for '{rpc_name}'")

        required = self._handler_authorities[rpc_name]
        if required == AuthorityType.SERVER_AUTHORITY and caller_authority != AuthorityType.SERVER_AUTHORITY:
            raise InvalidAuthorityError(
                f"Caller with authority {caller_authority} cannot execute server-authoritative RPC '{rpc_name}'"
            )

        handler = self._handlers[rpc_name]
        result = handler(message, context)

        # Store in idempotency cache
        self._idempotency_cache[message.operation_id] = result
        self._cached_order.append(message.operation_id)
        if len(self._cached_order) > self._max_cache_size:
            oldest = self._cached_order.pop(0)
            self._idempotency_cache.pop(oldest, None)

        return result

    @staticmethod
    def encode_message(message: RPCMessage) -> bytes:
        """Serialize RPCMessage to binary UTF-8 JSON bytes."""
        data = {
            "op_id": message.operation_id,
            "ns": message.target_net_id.namespace,
            "val": message.target_net_id.value,
            "name": message.rpc_name,
            "type": message.rpc_type.value,
            "payload": message.payload,
        }
        return json.dumps(data, separators=(",", ":")).encode("utf-8")

    @staticmethod
    def decode_message(data: bytes) -> RPCMessage:
        """Deserialize raw bytes into RPCMessage."""
        raw = json.loads(data.decode("utf-8"))
        return RPCMessage(
            operation_id=raw["op_id"],
            target_net_id=NetworkEntityId(namespace=raw["ns"], value=raw["val"]),
            rpc_name=raw["name"],
            rpc_type=RPCType(raw["type"]),
            payload=raw.get("payload", {}),
        )
