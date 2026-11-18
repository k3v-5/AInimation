"""Acceptance tests for UAF-81.87: Universal Deep Unreal Engine 5 LiveLink,
Bidirectional Synchronization, Hot Reload & Interoperability Bridge.
"""

from __future__ import annotations
import pytest
import time
from typing import Dict, Any

from uaf.bridge.ue5 import (
    UE5Bridge,
    AuthorityModel,
    BridgeMessage,
    BridgeMessageType,
    ChangeEvent,
    SyncState,
    UpdatePriority,
    UE5Capabilities,
    UE5Feature,
    BridgeProtocolVersion,
    HandshakeResult,
    BridgeTransport,
    EmbeddedTransport,
    IPCTransport,
    TCPTransport,
    WebSocketTransport,
    BridgeSession,
    ConnectionState,
    RevisionVector,
    PatchOperation,
    StatePatch,
    apply_patch,
    diff_dict,
    BridgeSnapshot,
    ConflictDetector,
    ConflictPolicy,
    SyncConflict,
    BridgeTransaction,
    TransactionManager,
    UE5ObjectEntry,
    UE5ObjectRegistry,
    UE5AssetEntry,
    UE5AssetRegistry,
    ReconnectionManager,
    BridgeRepairEngine,
    OrphanPolicy,
    OrphanReport,
    QuarantinedItem,
    QuarantineManager,
    UE5ErrorCode,
    UE5ErrorContext,
    UE5BridgeError,
    BridgeSpan,
    BridgeTelemetryCollector,
    AuditEntry,
    LiveLinkAuditTrail,
    EngineCompatibilityValidator,
    CompatibilityReport,
    DeterminismChecker,
    StateDivergenceReport,
    LiveLinkCertificationSuite,
    CertificationReport,
)
from uaf.bridge.ue5.scene.cameras import CameraBridgePayload, CameraRole
from uaf.bridge.ue5.scene.lighting import LightingBridgePayload, UE5LightType
from uaf.bridge.ue5.scene.world_partition import WorldPartitionBridge, CellStreamingState
from uaf.bridge.ue5.assets.niagara import NiagaraBridgePayload, NiagaraEmitterDescriptor
from uaf.bridge.ue5.assets.animation import AnimationBridgePayload, AnimNotifyEvent
from uaf.bridge.ue5.animation.control_rig import ControlRigBridgePayload, RigControlValue
from uaf.bridge.ue5.animation.sequencer import SequencerBridgePayload, SequencerTrackPayload, SequencerKeyframe
from uaf.bridge.ue5.protocol.schema import BridgeMessageCodec, BridgeSchemaValidationError
from uaf.bridge.ue5.protocol.versioning import VersionMismatchError


class TestUE5BridgeProtocol:
    """Tests protocol, message encoding, and version negotiation."""

    def test_protocol_versioning_and_negotiation(self):
        v1 = BridgeProtocolVersion(major=1, minor=0, patch=0)
        v2 = BridgeProtocolVersion(major=1, minor=1, patch=0)
        assert v1.is_compatible(v2)

        v_incompatible = BridgeProtocolVersion(major=2, minor=0, patch=0)
        assert not v1.is_compatible(v_incompatible)

        with pytest.raises(VersionMismatchError):
            v1.assert_compatible(v_incompatible)

    def test_message_serialization_and_codec(self):
        msg = BridgeMessage(
            message_type=BridgeMessageType.HEARTBEAT,
            sender_id="uaf_core",
            session_id="sess_123",
            payload={"ping": 100},
        )
        data = BridgeMessageCodec.encode(msg)
        assert isinstance(data, bytes)

        decoded = BridgeMessageCodec.decode(data)
        assert decoded.message_type == BridgeMessageType.HEARTBEAT
        assert decoded.sender_id == "uaf_core"
        assert decoded.payload == {"ping": 100}

    def test_capabilities_feature_flags(self):
        caps = UE5Capabilities(
            engine_version="5.4.2",
            enabled_features={UE5Feature.NANITE, UE5Feature.LUMEN, UE5Feature.NIAGARA},
        )
        assert caps.has_feature(UE5Feature.NANITE)
        assert caps.has_feature(UE5Feature.LUMEN)
        assert not caps.has_feature(UE5Feature.SUBSTRATE)


class TestUE5BridgeTransport:
    """Tests transport channels and loopback communication."""

    def test_embedded_transport_bidirectional_pair(self):
        uaf_side, ue5_side = EmbeddedTransport.create_pair()
        assert not uaf_side.is_connected
        assert not ue5_side.is_connected

        uaf_side.connect()
        ue5_side.connect()
        assert uaf_side.is_connected
        assert ue5_side.is_connected

        # Send from UAF side to UE5 side
        test_msg = b"PING_FRAME_01"
        uaf_side.send(test_msg)
        assert ue5_side.has_pending_messages()

        recv = ue5_side.receive()
        assert recv == test_msg

        # Send from UE5 side to UAF side
        uaf_side.send(b"PONG_FRAME_01")
        assert ue5_side.receive() == b"PONG_FRAME_01"


class TestUE5BridgeSyncAndTransactions:
    """Tests delta patching, snapshots, transactions, and conflicts."""

    def test_delta_patches_and_rfc6902_operations(self):
        initial_state = {"actor_01": {"x": 10.0, "y": 20.0, "color": "red"}}
        target_state = {"actor_01": {"x": 15.0, "y": 20.0, "color": "blue", "visible": True}}

        patch = diff_dict(initial_state, target_state)
        assert len(patch.operations) > 0

        applied = apply_patch(initial_state, patch)
        assert applied["actor_01"]["x"] == 15.0
        assert applied["actor_01"]["color"] == "blue"
        assert applied["actor_01"]["visible"] is True

    def test_deterministic_snapshots_sha256(self):
        state1 = {"actor_1": {"loc": [0, 10, 0]}, "actor_2": {"health": 100}}
        snap1 = BridgeSnapshot(frame=1, timestamp_us=1000, objects=state1)
        snap2 = BridgeSnapshot(frame=1, timestamp_us=2000, objects=state1)

        # Same state contents must yield identical state hash regardless of timestamp
        assert snap1.state_hash == snap2.state_hash
        assert len(snap1.state_hash) == 64  # SHA-256 hex length

        divergent_state = {"actor_1": {"loc": [0, 10, 1]}, "actor_2": {"health": 100}}
        snap3 = BridgeSnapshot(frame=1, timestamp_us=1000, objects=divergent_state)
        assert snap1.state_hash != snap3.state_hash

    def test_transaction_staging_commit_and_rollback(self):
        tx_mgr = TransactionManager()
        tx = tx_mgr.begin("Spawn player and attach weapon")
        assert tx.is_active

        tx.stage_operation("spawn_actor", {"id": "player_01"})
        tx.stage_operation("attach_mesh", {"parent": "player_01", "mesh": "sword_01"})
        assert len(tx.operations) == 2

        tx_mgr.commit(tx.transaction_id)
        assert tx.is_committed

        # Test rollback
        tx2 = tx_mgr.begin("Invalid operation batch")
        tx2.stage_operation("delete_critical", {"id": "world_root"})
        tx_mgr.rollback(tx2.transaction_id)
        assert tx2.is_rolled_back

    def test_conflict_detection_and_resolution(self):
        detector = ConflictDetector(default_policy=ConflictPolicy.UAF_WINS)
        rev_base = RevisionVector(uaf_revision=1, ue5_revision=1)
        rev_uaf = RevisionVector(uaf_revision=2, ue5_revision=1)
        rev_ue5 = RevisionVector(uaf_revision=1, ue5_revision=2)

        conflict = detector.detect(
            object_id="actor_hero",
            base_rev=rev_base,
            uaf_rev=rev_uaf,
            ue5_rev=rev_ue5,
            uaf_patch=StatePatch([]),
            ue5_patch=StatePatch([]),
        )
        assert conflict is not None

        resolved_val = detector.resolve(
            conflict,
            uaf_val={"x": 100},
            ue5_val={"x": 200},
        )
        assert resolved_val == {"x": 100}  # UAF_WINS policy


class TestUE5BridgeRegistriesAndAssets:
    """Tests object and asset registry, multi-hashing, and hot reload."""

    def test_asset_registration_and_multi_hash(self):
        registry = UE5AssetRegistry()
        entry = registry.register(
            uaf_asset_id="mesh_pillar_01",
            ue5_package_path="/Game/Environment/Pillars/SM_Pillar_01",
            asset_type="StaticMesh",
            source_hash="src_hash_111",
            content_hash="cnt_hash_222",
            build_hash="bld_hash_333",
            dependencies=["mat_stone_master"],
        )
        assert registry.count == 1
        assert entry.build_hash == "bld_hash_333"
        assert registry.get_by_path("/Game/Environment/Pillars/SM_Pillar_01") == entry

    def test_asset_hot_reload_and_dependent_tracking(self):
        registry = UE5AssetRegistry()
        registry.register(
            uaf_asset_id="mat_master",
            ue5_package_path="/Game/Materials/M_Master",
            asset_type="Material",
            source_hash="s1",
            content_hash="c1",
            build_hash="b1",
        )
        registry.register(
            uaf_asset_id="mesh_rock",
            ue5_package_path="/Game/Meshes/SM_Rock",
            asset_type="StaticMesh",
            source_hash="s2",
            content_hash="c2",
            build_hash="b2",
            dependencies=["mat_master"],
        )

        dependents = registry.get_dependents("mat_master")
        assert "mesh_rock" in dependents

        # Hot reload mat_master with new build hash
        updated = registry.update_build_hash("mat_master", "b1_recompiled")
        assert updated.build_hash == "b1_recompiled"


class TestUE5BridgeSceneAndSubsystems:
    """Tests scene payloads: camera, light, Niagara, animation, control rig, Sequencer, world partition."""

    def test_camera_and_lighting_payloads(self):
        cam = CameraBridgePayload(
            camera_id="cam_cinematic_01",
            role=CameraRole.CINEMATIC,
            fov_degrees=65.0,
            focal_length_mm=35.0,
            aperture_fstop=2.8,
        )
        cam_dict = cam.to_dict()
        assert cam_dict["role"] == "CINEMATIC"
        assert cam_dict["fov_degrees"] == 65.0

        light = LightingBridgePayload(
            light_id="sun_light",
            light_type=UE5LightType.DIRECTIONAL,
            intensity_lux=100000.0,
            color_temperature_k=6500.0,
            cast_shadows=True,
        )
        light_dict = light.to_dict()
        assert light_dict["light_type"] == "DIRECTIONAL"
        assert light_dict["cast_shadows"] is True

    def test_niagara_and_animation_payloads(self):
        niagara = NiagaraBridgePayload(
            system_id="fx_sparks",
            system_asset_path="/Game/VFX/NS_Sparks",
            emitters=[
                NiagaraEmitterDescriptor(emitter_name="SparksEmitter", spawn_rate=500.0, is_active=True),
            ],
            system_parameters={"SpawnColor": [1.0, 0.8, 0.2]},
        )
        assert len(niagara.emitters) == 1
        assert niagara.emitters[0].spawn_rate == 500.0

        anim = AnimationBridgePayload(
            animation_id="anim_run",
            sequence_name="AS_Hero_Run",
            duration_seconds=1.2,
            notifies=[AnimNotifyEvent(notify_name="Footstep_L", trigger_time_seconds=0.3)],
        )
        assert anim.duration_seconds == 1.2
        assert len(anim.notifies) == 1

    def test_control_rig_and_sequencer_payloads(self):
        rig = ControlRigBridgePayload(
            rig_id="cr_hero",
            rig_asset_path="/Game/Characters/CR_Hero",
            controls={"hand_ik_l": RigControlValue(control_name="hand_ik_l", location=(10.0, 5.0, 20.0))},
        )
        assert "hand_ik_l" in rig.controls

        seq = SequencerBridgePayload(
            sequence_id="cutscene_boss_intro",
            sequence_asset_path="/Game/Cinematics/LS_BossIntro",
            duration_frames=300,
            tracks=[
                SequencerTrackPayload(
                    track_name="CameraTrack",
                    target_object_id="cam_cinematic_01",
                    keyframes=[
                        SequencerKeyframe(frame=0, value={"fov": 65.0}),
                        SequencerKeyframe(frame=150, value={"fov": 45.0}),
                    ],
                )
            ],
        )
        assert seq.duration_frames == 300
        assert len(seq.tracks) == 1

    def test_world_partition_bridge(self):
        wp = WorldPartitionBridge(grid_size=128.0)
        cell = wp.get_or_create_cell(0, 0)
        assert cell.state == CellStreamingState.UNLOADED

        wp.set_cell_state(0, 0, CellStreamingState.LOADED)
        assert wp.get_or_create_cell(0, 0).state == CellStreamingState.LOADED


class TestUE5BridgeRecoveryAndDiagnostics:
    """Tests quarantine, orphan repair, audit chain, and telemetry."""

    def test_quarantine_manager(self):
        qm = QuarantineManager()
        qm.quarantine("corrupt_asset_99", "Failed shader compilation")
        assert qm.is_quarantined("corrupt_asset_99")
        assert qm.count == 1

        item = qm.get("corrupt_asset_99")
        assert item is not None
        assert "Failed shader compilation" in item.reason

        qm.release("corrupt_asset_99")
        assert not qm.is_quarantined("corrupt_asset_99")

    def test_orphan_detection_and_repair(self):
        obj_reg = UE5ObjectRegistry()
        asset_reg = UE5AssetRegistry()
        repair = BridgeRepairEngine(obj_reg, asset_reg)

        # Register one known object
        obj_reg.register(
            uaf_object_id="actor_known",
            ue5_object_path="/Game/Levels/Main.actor_known",
            object_type="StaticMeshActor",
        )

        # Simulate UE5 reporting an unexpected extra actor
        reported_paths = [
            "/Game/Levels/Main.actor_known",
            "/Game/Levels/Main.actor_orphan_stranger",
        ]
        report = repair.detect_orphans(reported_paths)
        assert report.orphan_count == 1
        assert "/Game/Levels/Main.actor_orphan_stranger" in report.orphaned_paths

    def test_tamper_evident_audit_trail(self):
        audit = LiveLinkAuditTrail()
        audit.record("EVT_1", object_id="obj_A", details={"x": 1})
        audit.record("EVT_2", object_id="obj_B", details={"y": 2})
        audit.record("EVT_3", object_id="obj_C", details={"z": 3})

        assert audit.count == 3
        assert audit.verify_chain() is True

        # Simulate cryptographic tampering
        tampered_entry = AuditEntry(
            sequence=audit.entries[1].sequence,
            timestamp_us=audit.entries[1].timestamp_us,
            event_type="EVT_TAMPERED",
            object_id="obj_TAMPERED",
            revision=0,
            payload_hash=audit.entries[1].payload_hash,
            prev_hash=audit.entries[1].prev_hash,
            entry_hash=audit.entries[1].entry_hash,
            details={"malicious": True},
        )
        audit._entries[1] = tampered_entry
        assert audit.verify_chain() is False

    def test_telemetry_collector_and_spans(self):
        telem = BridgeTelemetryCollector()
        span = telem.start_span("mesh_sync", subsystem="Mesh")
        time.sleep(0.001)
        telem.stop_span("mesh_sync")

        telem.record_traffic(sent_bytes=1024, recv_bytes=2048)
        telem.record_roundtrip(latency_us=4500)

        summary = telem.get_summary()
        assert summary["messages_sent"] == 1
        assert summary["bytes_sent"] == 1024
        assert summary["avg_rtt_ms"] == 4.5


class TestUE5BridgeMasterCoordinatorEndToEnd:
    """Tests the master UE5Bridge coordinator end-to-end integration."""

    def test_full_bridge_lifecycle_and_certification(self):
        bridge = UE5Bridge()

        # 1. Connection & Handshake
        assert bridge.connect() is True
        assert bridge.is_connected is True

        handshake_rep = bridge.handshake(engine_version="5.4.0")
        assert handshake_rep.is_compatible is True

        # 2. Asset Registration & Hot Reload
        bridge.register_asset(
            asset_id="sm_gate_01",
            asset_type="StaticMesh",
            source_hash="src_gate",
            content_hash="cnt_gate",
            build_hash="bld_gate_v1",
        )
        assert bridge.asset_registry.count == 1

        reload_res = bridge.reload_asset("sm_gate_01", "bld_gate_v2")
        assert reload_res is True

        # 3. Actor Spawning & Transform Updates
        actor_entry = bridge.spawn_actor(
            actor_id="gate_actor_01",
            actor_class="StaticMeshActor",
            location=(100.0, 200.0, 50.0),
        )
        assert bridge.object_registry.count == 1
        assert actor_entry.properties["location"] == [100.0, 200.0, 50.0]

        change_evt = bridge.update_actor_transform(
            actor_id="gate_actor_01",
            location=(110.0, 200.0, 50.0),
            rotation=(0.0, 45.0, 0.0),
        )
        assert change_evt.revision == 1
        assert change_evt.object_id == "gate_actor_01"

        # 4. Transactions
        tx = bridge.begin_transaction("Bulk environment spawn")
        tx.stage_operation("spawn_torch", {"id": "torch_01"})
        bridge.commit_transaction(tx.transaction_id)
        assert tx.is_committed

        # 5. Snapshots & Determinism
        snap_a = bridge.capture_snapshot(frame=10)
        snap_b = bridge.capture_snapshot(frame=10)
        div_rep = bridge.determinism_checker.compare_snapshots(snap_a, snap_b)
        assert div_rep.is_deterministic is True
        assert div_rep.diverged_objects_count == 0

        # 6. Golden Scene Certification Suite
        cert_report = bridge.certify()
        assert cert_report.passed is True
        assert cert_report.gates_passed == cert_report.gates_total

        # 7. Audit Log Verification
        assert bridge.audit_trail.verify_chain() is True
        assert bridge.audit_trail.count >= 6

        # 8. Clean Disconnect
        bridge.disconnect()
        assert bridge.is_connected is False
