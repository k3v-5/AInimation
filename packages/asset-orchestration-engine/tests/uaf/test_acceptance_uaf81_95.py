"""
UAF-81.95: Real-Time In-Engine Co-Piloting & Live Synchronization
Acceptance Test Suite.
Verifies unit conversions, message serialization roundtrips, session lifecycles,
reconciler conflict resolution (Designer Lock Wins), terrain delta patching,
and sub-500ms dispatch latency.
"""

import json
import math
import pytest
from typing import Dict

from uaf.copilot import (
    CopilotSessionState,
    SyncDirection,
    CoPilotCommandType,
    ConflictResolutionPolicy,
    Vector3D,
    Rotator3D,
    Transform3D,
    LiveActorSync,
    TerrainRegionPatch,
    CoPilotMessage,
    CoPilotSessionMetrics,
    serialize_message,
    deserialize_message,
    MessageBuilder,
    CoPilotReconciler,
    CoPilotDaemonServer,
    UE5CoPilotListener,
)


class TestCoPilotCoreAndMath:
    """Verifies coordinate transforms and unit conversion between AOE and UE5."""

    def test_meters_to_centimeters_conversion(self):
        v = Vector3D(x=12.5, y=-4.0, z=1.75)
        cm_tuple = v.to_ue5_cm()
        assert cm_tuple == (1250.0, -400.0, 175.0)

    def test_centimeters_to_meters_conversion(self):
        v = Vector3D.from_ue5_cm(1250.0, -400.0, 175.0)
        assert v.x == 12.5
        assert v.y == -4.0
        assert v.z == 1.75

    def test_vector_distance(self):
        v1 = Vector3D(x=0.0, y=0.0, z=0.0)
        v2 = Vector3D(x=3.0, y=4.0, z=0.0)
        assert math.isclose(v1.distance_to(v2), 5.0, abs_tol=1e-3)


class TestMessageProtocol:
    """Verifies message construction, serialization, and roundtrip deserialization."""

    def test_handshake_roundtrip(self):
        msg = MessageBuilder.build_handshake(sender="UE5_EDITOR_CLIENT")
        serialized = serialize_message(msg)
        restored = deserialize_message(serialized)

        assert restored.command_type == CoPilotCommandType.HANDSHAKE
        assert restored.sender == "UE5_EDITOR_CLIENT"
        assert restored.payload["status"] == "READY"
        assert "terrain_sync" in restored.payload["capabilities"]

    def test_terrain_patch_message(self):
        patch = TerrainRegionPatch(
            patch_id="patch_crater_01",
            start_x=10,
            start_y=10,
            width=4,
            height=4,
            height_samples_m=[0.0] * 16,
            weightmap_layer="Rock",
        )
        msg = MessageBuilder.build_terrain_sync(patch)
        serialized = serialize_message(msg)
        restored = deserialize_message(serialized)

        assert restored.command_type == CoPilotCommandType.SYNC_TERRAIN_REGION
        assert restored.payload["patch_id"] == "patch_crater_01"
        assert restored.payload["width"] == 4

    def test_feedback_transform_message(self):
        t = Transform3D(
            position=Vector3D(x=10.0, y=20.0, z=0.0),
            rotation=Rotator3D(yaw=90.0),
        )
        msg = MessageBuilder.build_feedback_transform(
            actor_id="Spawner_Boss_01",
            new_transform=t,
            lock_designer=True,
        )
        serialized = serialize_message(msg)
        restored = deserialize_message(serialized)

        assert restored.command_type == CoPilotCommandType.FEEDBACK_TRANSFORM_CHANGED
        assert restored.payload["actor_id"] == "Spawner_Boss_01"
        assert restored.payload["lock_designer"] is True
        assert restored.payload["transform"]["position"]["x"] == 10.0


class TestCoPilotReconcilerAndConcurrency:
    """Verifies state arbitration, Designer Lock enforcement, and conflict resolution."""

    def test_procedural_update_application(self):
        reconciler = CoPilotReconciler()
        actor = LiveActorSync(
            actor_id="Enemy_Patrol_1",
            actor_class="Character",
            transform=Transform3D(position=Vector3D(x=5.0, y=5.0, z=0.0)),
        )
        applied, status = reconciler.apply_procedural_update(actor)
        assert applied is True
        assert status == "APPLIED"
        assert reconciler.get_actor("Enemy_Patrol_1").revision == 1

    def test_designer_lock_wins_conflict_resolution(self):
        # Default policy: DESIGNER_LOCK_WINS
        reconciler = CoPilotReconciler(conflict_policy=ConflictResolutionPolicy.DESIGNER_LOCK_WINS)

        # 1. Designer moves actor manually and locks it
        designer_transform = Transform3D(position=Vector3D(x=50.0, y=50.0, z=2.0))
        reconciler.apply_designer_feedback(
            actor_id="Door_AirLock_01",
            new_transform=designer_transform,
            lock_designer=True,
        )
        assert "Door_AirLock_01" in reconciler.designer_locks

        # 2. AOE procedural regeneration tries to move the door back to (0, 0, 0)
        procedural_attempt = LiveActorSync(
            actor_id="Door_AirLock_01",
            actor_class="Door",
            transform=Transform3D(position=Vector3D(x=0.0, y=0.0, z=0.0)),
        )
        applied, status = reconciler.apply_procedural_update(procedural_attempt)

        # Procedural change must be rejected; designer's position is preserved!
        assert applied is False
        assert status == "PRESERVED_DESIGNER_LOCK"
        saved = reconciler.get_actor("Door_AirLock_01")
        assert saved.transform.position.x == 50.0
        assert saved.transform.position.y == 50.0
        assert reconciler.metrics.conflicts_resolved == 1

    def test_procedural_override_policy(self):
        reconciler = CoPilotReconciler(conflict_policy=ConflictResolutionPolicy.PROCEDURAL_OVERRIDE)
        # Designer locked actor
        reconciler.apply_designer_feedback("SpikeTrap_1", Transform3D(position=Vector3D(x=10.0, y=10.0, z=0.0)), lock_designer=True)
        assert "SpikeTrap_1" in reconciler.designer_locks

        # Procedural override forced
        proc_actor = LiveActorSync(
            actor_id="SpikeTrap_1",
            actor_class="Trap",
            transform=Transform3D(position=Vector3D(x=99.0, y=99.0, z=0.0)),
        )
        applied, status = reconciler.apply_procedural_update(proc_actor)
        assert applied is True
        assert status == "PROCEDURAL_OVERRIDE_APPLIED"
        assert reconciler.get_actor("SpikeTrap_1").transform.position.x == 99.0

    def test_explicit_unlock(self):
        reconciler = CoPilotReconciler()
        reconciler.apply_designer_feedback("Light_01", Transform3D(), lock_designer=True)
        assert "Light_01" in reconciler.designer_locks

        assert reconciler.unlock_actor("Light_01") is True
        assert "Light_01" not in reconciler.designer_locks


class TestCoPilotDaemonServer:
    """Verifies server lifecycle, message dispatching, and latency bounds."""

    def test_daemon_lifecycle_and_handshake(self):
        server = CoPilotDaemonServer(port=27182)
        assert server.state == CopilotSessionState.IDLE

        server.start_listening()
        assert server.state == CopilotSessionState.LISTENING

        # Dispatch Handshake
        handshake_msg = MessageBuilder.build_handshake(sender="UE5_WORKSTATION_1")
        reply = server.process_incoming_message(handshake_msg)

        assert reply.command_type == CoPilotCommandType.ACK
        assert server.state == CopilotSessionState.CONNECTED
        assert server.connected_client_id == "UE5_WORKSTATION_1"

    def test_ping_pong_and_sub_500ms_latency(self):
        server = CoPilotDaemonServer()
        server.start_listening()

        ping_msg = MessageBuilder.build_ping(sender="UE5_CLIENT")
        reply = server.process_incoming_message(ping_msg)

        assert reply.command_type == CoPilotCommandType.PONG
        assert reply.payload["reply_to_id"] == ping_msg.message_id
        # Average latency must strictly satisfy <= 500ms
        assert server.reconciler.metrics.average_latency_ms <= 500.0

    def test_spawner_sync_dispatch(self):
        server = CoPilotDaemonServer()
        server.start_listening()

        actors = [
            LiveActorSync(
                actor_id=f"Mob_{i}",
                actor_class="EnemyPawn",
                transform=Transform3D(position=Vector3D(x=float(i), y=0.0, z=0.0)),
            )
            for i in range(5)
        ]
        sync_msg = MessageBuilder.build_actor_sync(actors, sender="AOE_MISSION_DIRECTOR")
        reply = server.process_incoming_message(sync_msg)

        assert reply.command_type == CoPilotCommandType.ACK
        assert reply.payload["applied_count"] == 5
        assert server.state == CopilotSessionState.SYNCING


class TestUE5CoPilotListener:
    """Verifies the in-editor companion listener and editor script."""

    def test_listener_actor_sync_processing(self):
        listener = UE5CoPilotListener()
        actors = [
            LiveActorSync(actor_id="Terminal_01", actor_class="StaticMeshActor", transform=Transform3D())
        ]
        msg = MessageBuilder.build_actor_sync(actors)
        raw_json = serialize_message(msg)

        ack_json = listener.handle_incoming_sync_command(raw_json)
        ack_msg = deserialize_message(ack_json)

        assert ack_msg.command_type == CoPilotCommandType.ACK
        assert "Terminal_01" in listener.applied_actors

    def test_report_designer_actor_moved(self):
        listener = UE5CoPilotListener()
        feedback_msg = listener.report_designer_actor_moved(
            actor_id="Cover_Barrier_02",
            location_cm=(1500.0, -250.0, 50.0),
            rotation_deg=(0.0, 45.0, 0.0),
            lock_designer=True,
        )
        assert feedback_msg.command_type == CoPilotCommandType.FEEDBACK_TRANSFORM_CHANGED
        assert feedback_msg.payload["actor_id"] == "Cover_Barrier_02"
        # 1500cm -> 15m, -250cm -> -2.5m
        assert feedback_msg.payload["transform"]["position"]["x"] == 15.0
        assert feedback_msg.payload["transform"]["position"]["y"] == -2.5

    def test_generate_editor_runner_script(self):
        script = UE5CoPilotListener.generate_editor_runner_script()
        assert "unreal" in script
        assert "EditorCoPilotRunner" in script
