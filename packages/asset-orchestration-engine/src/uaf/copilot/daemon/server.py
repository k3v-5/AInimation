"""
UAF-81.95: Co-Pilot Daemon Headless Dispatcher & Session Server.
Manages bidirectional client connections, command routing, and telemetry.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from uaf.copilot.core.contracts import (
    CoPilotCommandType,
    CoPilotMessage,
    CopilotSessionState,
    LiveActorSync,
    TerrainRegionPatch,
    Transform3D,
    Vector3D,
    Rotator3D,
)
from uaf.copilot.protocol.messages import MessageBuilder
from uaf.copilot.sync.reconciler import CoPilotReconciler


class CoPilotDaemonServer:
    """
    Headless daemon service dispatching synchronization commands between
    AOE generative modules and the connected Unreal Engine 5 Editor instance.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 27182,
        reconciler: Optional[CoPilotReconciler] = None,
    ):
        self.host = host
        self.port = port
        self.reconciler = reconciler or CoPilotReconciler()
        self.state = CopilotSessionState.IDLE
        self.connected_client_id: Optional[str] = None
        self.session_start_time: float = 0.0

    def start_listening(self) -> bool:
        """Starts the daemon in listening state."""
        self.state = CopilotSessionState.LISTENING
        self.session_start_time = time.time()
        return True

    def stop(self) -> None:
        """Stops the daemon and closes sessions."""
        self.state = CopilotSessionState.DISCONNECTED
        self.connected_client_id = None

    def process_incoming_message(self, message: CoPilotMessage) -> CoPilotMessage:
        """
        Dispatches incoming message from client (or local test harness),
        updates internal registries, and returns a strictly typed response.
        """
        start_time = time.time()
        self.reconciler.metrics.messages_received += 1

        cmd = message.command_type
        reply: CoPilotMessage

        if cmd == CoPilotCommandType.HANDSHAKE:
            self.state = CopilotSessionState.CONNECTED
            self.connected_client_id = message.sender
            reply = MessageBuilder.build_ack(
                reply_to_id=message.message_id,
                sender="AOE_COPILOT_DAEMON",
                details={
                    "session_state": self.state.value,
                    "host": self.host,
                    "port": self.port,
                },
            )

        elif cmd == CoPilotCommandType.PING:
            reply = MessageBuilder.build_pong(
                reply_to_id=message.message_id,
                sender="AOE_COPILOT_DAEMON",
            )

        elif cmd == CoPilotCommandType.SYNC_TERRAIN_REGION:
            patch = TerrainRegionPatch(**message.payload)
            self.reconciler.apply_terrain_patch(patch)
            self.state = CopilotSessionState.SYNCING
            reply = MessageBuilder.build_ack(
                reply_to_id=message.message_id,
                sender="AOE_COPILOT_DAEMON",
                details={"patch_id": patch.patch_id, "status": "TERRAIN_PATCHED"},
            )

        elif cmd == CoPilotCommandType.SYNC_SPAWNER_AI:
            actors_data = message.payload.get("actors", [])
            applied_count = 0
            for a_dict in actors_data:
                actor = LiveActorSync(**a_dict)
                applied, _ = self.reconciler.apply_procedural_update(actor)
                if applied:
                    applied_count += 1
            self.state = CopilotSessionState.SYNCING
            reply = MessageBuilder.build_ack(
                reply_to_id=message.message_id,
                sender="AOE_COPILOT_DAEMON",
                details={"applied_count": applied_count, "total": len(actors_data)},
            )

        elif cmd == CoPilotCommandType.FEEDBACK_TRANSFORM_CHANGED:
            actor_id = message.payload.get("actor_id", "")
            raw_t = message.payload.get("transform", {})
            lock_designer = message.payload.get("lock_designer", True)

            pos = Vector3D(**raw_t.get("position", {}))
            rot = Rotator3D(**raw_t.get("rotation", {}))
            scale = Vector3D(**raw_t.get("scale", {"x": 1.0, "y": 1.0, "z": 1.0}))
            transform = Transform3D(position=pos, rotation=rot, scale=scale)

            updated = self.reconciler.apply_designer_feedback(
                actor_id=actor_id,
                new_transform=transform,
                lock_designer=lock_designer,
            )
            reply = MessageBuilder.build_ack(
                reply_to_id=message.message_id,
                sender="AOE_COPILOT_DAEMON",
                details={
                    "actor_id": updated.actor_id,
                    "revision": updated.revision,
                    "is_locked": updated.is_locked_by_designer,
                },
            )

        elif cmd == CoPilotCommandType.FEEDBACK_DESIGNER_LOCK:
            actor_id = message.payload.get("actor_id", "")
            lock = message.payload.get("lock", True)
            if not lock:
                self.reconciler.unlock_actor(actor_id)
            elif actor_id in self.reconciler.actors:
                self.reconciler.actors[actor_id].is_locked_by_designer = True
                self.reconciler.designer_locks.add(actor_id)
            reply = MessageBuilder.build_ack(
                reply_to_id=message.message_id,
                sender="AOE_COPILOT_DAEMON",
                details={"actor_id": actor_id, "locked": lock},
            )

        else:
            reply = MessageBuilder.build_error(
                reply_to_id=message.message_id,
                error_message=f"Unknown or unhandled command: {cmd.value}",
                sender="AOE_COPILOT_DAEMON",
            )

        elapsed_ms = (time.time() - start_time) * 1000.0
        self.reconciler.record_latency(elapsed_ms)
        self.reconciler.metrics.messages_sent += 1
        return reply
