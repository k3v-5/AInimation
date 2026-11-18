"""
UAF-81.83: Semantic and Security Validator for Networking, Replication & Input.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List

from ..engine.server import DedicatedServerEngine
from ..models.definition import (
    InputCommand,
    NetworkEntityId,
    Packet,
    PacketHeader,
)


@dataclass(frozen=True)
class NetworkValidationIssue:
    severity: str  # "ERROR", "WARNING"
    code: str
    message: str
    context: str = ""


class UniversalRuntimeNetworkingValidator:
    """Semantic validation engine verifying protocol conformance, numeric safety, and integrity."""

    @classmethod
    def validate_server(cls, server: DedicatedServerEngine) -> List[NetworkValidationIssue]:
        issues: List[NetworkValidationIssue] = []

        if server.session.tick_rate <= 0:
            issues.append(
                NetworkValidationIssue(
                    "ERROR",
                    "NET_INVALID_TICK_RATE",
                    f"Server tick rate must be positive, got {server.session.tick_rate}",
                    server.session.session_id,
                )
            )

        # Validate authoritative entities
        for net_id, props in server.entities.items():
            if net_id.namespace < 0 or net_id.value < 0:
                issues.append(
                    NetworkValidationIssue(
                        "ERROR",
                        "NET_INVALID_ENTITY_ID",
                        f"Negative identifier values in {net_id}",
                        str(net_id),
                    )
                )

            # Check numeric safety in properties
            for prop_name, val in props.items():
                if isinstance(val, (int, float)):
                    if math.isnan(val) or math.isinf(val):
                        issues.append(
                            NetworkValidationIssue(
                                "ERROR",
                                "NET_NUMERIC_ERROR",
                                f"Non-finite property {prop_name}={val} in entity {net_id}",
                                str(net_id),
                            )
                        )
                elif isinstance(val, (list, tuple)) and len(val) == 3 and all(isinstance(x, (int, float)) for x in val):
                    for idx, c in enumerate(val):
                        if math.isnan(c) or math.isinf(c):
                            issues.append(
                                NetworkValidationIssue(
                                    "ERROR",
                                    "NET_NUMERIC_ERROR",
                                    f"Non-finite coordinate in {prop_name}[{idx}]={c} in entity {net_id}",
                                    str(net_id),
                                )
                            )

        # Validate connections
        for conn_id, conn in server.connections.items():
            if not conn.connection_id or not conn.client_id:
                issues.append(
                    NetworkValidationIssue(
                        "ERROR",
                        "NET_EMPTY_CONNECTION_ID",
                        f"Empty connection_id or client_id in connection {conn_id}",
                        conn_id,
                    )
                )

        return issues

    @classmethod
    def validate_input(cls, cmd: InputCommand) -> List[NetworkValidationIssue]:
        issues: List[NetworkValidationIssue] = []

        if cmd.sequence < 0:
            issues.append(
                NetworkValidationIssue(
                    "ERROR",
                    "NET_INVALID_SEQUENCE",
                    f"InputCommand sequence cannot be negative: {cmd.sequence}",
                    str(cmd.sequence),
                )
            )

        for idx, ax in enumerate(cmd.axes):
            if math.isnan(ax) or math.isinf(ax):
                issues.append(
                    NetworkValidationIssue(
                        "ERROR",
                        "NET_NUMERIC_ERROR",
                        f"Non-finite axis value at index {idx}: {ax}",
                        str(cmd.sequence),
                    )
                )

        return issues
