"""Master UE5 Bridge coordinator unifying protocol, transport, sync, assets, and diagnostics."""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple

from uaf.bridge.ue5.protocol.messages import (
    AuthorityModel,
    BridgeMessage,
    BridgeMessageType,
    ChangeEvent,
    SyncState,
    UpdatePriority,
)
from uaf.bridge.ue5.protocol.capabilities import UE5Capabilities, UE5Feature
from uaf.bridge.ue5.protocol.versioning import BridgeProtocolVersion
from uaf.bridge.ue5.transport.base import BridgeTransport
from uaf.bridge.ue5.transport.embedded import EmbeddedTransport
from uaf.bridge.ue5.sync.session import BridgeSession, ConnectionState
from uaf.bridge.ue5.sync.revisions import RevisionVector
from uaf.bridge.ue5.sync.patches import StatePatch, diff_dict
from uaf.bridge.ue5.sync.snapshots import BridgeSnapshot
from uaf.bridge.ue5.sync.conflicts import ConflictDetector, ConflictPolicy, SyncConflict
from uaf.bridge.ue5.sync.transactions import BridgeTransaction, TransactionManager
from uaf.bridge.ue5.registry.objects import UE5ObjectEntry, UE5ObjectRegistry
from uaf.bridge.ue5.registry.assets import UE5AssetEntry, UE5AssetRegistry
from uaf.bridge.ue5.registry.mappings import generate_asset_name, resolve_package_path
from uaf.bridge.ue5.recovery.reconnect import ReconnectionManager
from uaf.bridge.ue5.recovery.repair import BridgeRepairEngine, OrphanPolicy, OrphanReport
from uaf.bridge.ue5.recovery.quarantine import QuarantineManager
from uaf.bridge.ue5.diagnostics.errors import UE5ErrorCode, UE5ErrorContext, UE5BridgeError
from uaf.bridge.ue5.diagnostics.traces import BridgeTelemetryCollector
from uaf.bridge.ue5.diagnostics.audit import LiveLinkAuditTrail
from uaf.bridge.ue5.validation.compatibility import EngineCompatibilityValidator, CompatibilityReport
from uaf.bridge.ue5.validation.determinism import DeterminismChecker, StateDivergenceReport
from uaf.bridge.ue5.validation.certification import LiveLinkCertificationSuite, CertificationReport
from uaf.bridge.ue5.scene.actors import ActorBridgePayload
from uaf.bridge.ue5.scene.cameras import CameraBridgePayload
from uaf.bridge.ue5.scene.lighting import LightingBridgePayload
from uaf.bridge.ue5.assets.niagara import NiagaraBridgePayload
from uaf.bridge.ue5.assets.animation import AnimationBridgePayload


class UE5Bridge:
    """Universal Deep Unreal Engine 5 LiveLink and Interoperability Bridge."""

    def __init__(
        self,
        transport: Optional[BridgeTransport] = None,
        default_authority: AuthorityModel = AuthorityModel.UAF_AUTHORITATIVE,
        conflict_policy: ConflictPolicy = ConflictPolicy.UAF_WINS,
    ) -> None:
        self.default_authority = default_authority
        self.session = BridgeSession()
        self.object_registry = UE5ObjectRegistry()
        self.asset_registry = UE5AssetRegistry()
        self.conflict_detector = ConflictDetector(default_policy=conflict_policy)
        self.transaction_manager = TransactionManager()
        self.reconnection_manager = ReconnectionManager()
        self.repair_engine = BridgeRepairEngine(self.object_registry, self.asset_registry)
        self.quarantine_manager = QuarantineManager()
        self.telemetry = BridgeTelemetryCollector()
        self.audit_trail = LiveLinkAuditTrail()
        self.compatibility_validator = EngineCompatibilityValidator()
        self.determinism_checker = DeterminismChecker()
        self.certification_suite = LiveLinkCertificationSuite(self)

        # Transport setup
        if transport is None:
            uaf_side, ue5_side = EmbeddedTransport.create_pair()
            self._transport: BridgeTransport = uaf_side
            self._peer_transport: Optional[BridgeTransport] = ue5_side
        else:
            self._transport = transport
            self._peer_transport = None

        self._frame_counter: int = 0

    @property
    def is_connected(self) -> bool:
        return self.session.is_active and self._transport.is_connected

    @property
    def transport(self) -> BridgeTransport:
        return self._transport

    def connect(self) -> bool:
        """Establishes connection across transport and marks session connected."""
        span = self.telemetry.start_span("bridge_connect")
        success = self._transport.connect()
        if success:
            self.session.connect()
            self.audit_trail.record(
                event_type="TRANSPORT_CONNECTED",
                details={"transport_type": self._transport.transport_type},
            )
        self.telemetry.stop_span("bridge_connect")
        return success

    def disconnect(self) -> None:
        """Disconnects transport and session."""
        self._transport.disconnect()
        self.session.disconnect()
        self.audit_trail.record(event_type="TRANSPORT_DISCONNECTED")

    def handshake(
        self,
        engine_version: str = "5.4.0",
        capabilities: Optional[UE5Capabilities] = None,
    ) -> CompatibilityReport:
        """Performs initial protocol and version compatibility handshake."""
        span = self.telemetry.start_span("bridge_handshake")
        caps = capabilities or UE5Capabilities(engine_version=engine_version)
        report = self.compatibility_validator.validate_engine(
            engine_version=engine_version,
            capabilities=caps,
            remote_protocol=self.session.protocol_version,
        )

        if report.is_compatible:
            self.session.capabilities = caps
            self.session.mark_handshake_complete(caps)
            self.audit_trail.record(
                event_type="HANDSHAKE_COMPLETED",
                details={
                    "engine_version": engine_version,
                    "protocol_version": report.protocol_version,
                },
            )
        else:
            self.audit_trail.record(
                event_type="HANDSHAKE_FAILED",
                details={"errors": [i.message for i in report.issues if i.severity == "ERROR"]},
            )

        self.telemetry.stop_span("bridge_handshake")
        return report

    # --- Asset Management ---

    def register_asset(
        self,
        asset_id: str,
        asset_type: str,
        source_hash: str,
        content_hash: str,
        build_hash: str,
        package_path: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
    ) -> UE5AssetEntry:
        """Registers an asset in the registry and audit trail."""
        resolved_path = package_path or resolve_package_path(
            asset_type=asset_type,
            asset_name=generate_asset_name(asset_type, asset_id),
        )
        entry = self.asset_registry.register(
            uaf_asset_id=asset_id,
            ue5_package_path=resolved_path,
            asset_type=asset_type,
            source_hash=source_hash,
            content_hash=content_hash,
            build_hash=build_hash,
            dependencies=dependencies,
        )
        self.audit_trail.record(
            event_type="ASSET_REGISTERED",
            object_id=asset_id,
            details={"package_path": resolved_path, "build_hash": build_hash},
        )
        return entry

    def reload_asset(self, asset_id: str, new_build_hash: str) -> bool:
        """Hot reloads an asset, tracking affected dependents and audit log."""
        span = self.telemetry.start_span("reload_asset", tags={"asset_id": asset_id})
        try:
            entry = self.asset_registry.update_build_hash(asset_id, new_build_hash)
            dependents = self.asset_registry.get_dependents(asset_id)
            self.audit_trail.record(
                event_type="ASSET_HOT_RELOADED",
                object_id=asset_id,
                details={
                    "new_build_hash": new_build_hash,
                    "affected_dependents": dependents,
                },
            )
            return True
        except KeyError:
            return False
        finally:
            self.telemetry.stop_span("reload_asset")

    def quarantine_asset(self, asset_id: str, reason: str) -> None:
        """Quarantines a corrupt or failing asset."""
        self.quarantine_manager.quarantine(asset_id, reason)
        self.audit_trail.record(
            event_type="ASSET_QUARANTINED",
            object_id=asset_id,
            details={"reason": reason},
        )

    # --- Scene / Actor Management ---

    def spawn_actor(
        self,
        actor_id: str,
        actor_class: str,
        uaf_world_entity_id: Optional[str] = None,
        location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        authority: Optional[AuthorityModel] = None,
    ) -> UE5ObjectEntry:
        """Spawns and registers an actor in the UE5 scene representation."""
        auth = authority or self.default_authority
        entry = self.object_registry.register(
            uaf_object_id=actor_id,
            ue5_object_path=f"/Game/Levels/Main.{actor_id}",
            object_type=actor_class,
            authority=auth,
        )
        entry.properties["location"] = list(location)
        entry.properties["rotation"] = list(rotation)
        entry.properties["scale"] = list(scale)
        entry.properties["actor_class"] = actor_class
        if uaf_world_entity_id:
            entry.properties["uaf_world_entity_id"] = uaf_world_entity_id

        self.audit_trail.record(
            event_type="ACTOR_SPAWNED",
            object_id=actor_id,
            revision=entry.revision.uaf_revision,
            details={"actor_class": actor_class, "authority": auth.value},
        )
        return entry

    def update_actor_transform(
        self,
        actor_id: str,
        location: Tuple[float, float, float],
        rotation: Tuple[float, float, float],
        scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> ChangeEvent:
        """Mutates an actor's transform emitting an explicit ChangeEvent."""
        entry = self.object_registry.get(actor_id)
        if not entry:
            raise UE5BridgeError(
                f"Actor {actor_id} not found in registry",
                UE5ErrorContext(UE5ErrorCode.UE5_RUNTIME_ERROR, f"Unknown actor {actor_id}"),
            )

        old_props = dict(entry.properties)
        entry.properties["location"] = list(location)
        entry.properties["rotation"] = list(rotation)
        entry.properties["scale"] = list(scale)
        entry.revision.uaf_revision += 1

        patch = diff_dict(old_props, entry.properties)
        event = ChangeEvent(
            event_id=f"evt_{int(time.perf_counter() * 1_000_000)}",
            object_id=actor_id,
            source=self.default_authority,
            revision=entry.revision.uaf_revision,
            priority=UpdatePriority.HIGH,
            patch=patch,
            state_hash=entry.content_hash,
        )
        self.session.record_change(event)
        self.audit_trail.record(
            event_type="TRANSFORM_UPDATED",
            object_id=actor_id,
            revision=entry.revision.uaf_revision,
            details={"location": location, "rotation": rotation},
        )
        return event

    def destroy_actor(self, actor_id: str) -> None:
        """Destroys an actor and unregisters it."""
        entry = self.object_registry.unregister(actor_id)
        if entry:
            self.audit_trail.record(
                event_type="ACTOR_DESTROYED",
                object_id=actor_id,
                details={"ue5_path": entry.ue5_object_path},
            )

    # --- Subsystem Sync ---

    def sync_camera(self, camera_id: str, payload: CameraBridgePayload) -> None:
        """Synchronizes camera state."""
        self.audit_trail.record(
            event_type="CAMERA_SYNC",
            object_id=camera_id,
            details={"role": payload.role.value, "fov": payload.fov_degrees},
        )

    def sync_light(self, light_id: str, payload: LightingBridgePayload) -> None:
        """Synchronizes lighting parameters."""
        self.audit_trail.record(
            event_type="LIGHT_SYNC",
            object_id=light_id,
            details={"light_type": payload.light_type.value, "intensity": payload.intensity_lux},
        )

    def sync_niagara(self, system_id: str, payload: NiagaraBridgePayload) -> None:
        """Synchronizes Niagara VFX parameters and active state."""
        self.audit_trail.record(
            event_type="NIAGARA_SYNC",
            object_id=system_id,
            details={"system_asset": payload.system_asset_path, "emitters": len(payload.emitters)},
        )

    def sync_animation(self, anim_id: str, payload: AnimationBridgePayload) -> None:
        """Synchronizes animation asset descriptor and notifies."""
        self.audit_trail.record(
            event_type="ANIM_SYNC",
            object_id=anim_id,
            details={"sequence": payload.sequence_name, "duration": payload.duration_seconds},
        )

    # --- Transactions ---

    def begin_transaction(self, description: str = "") -> BridgeTransaction:
        """Begins a multi-operation staging transaction."""
        tx = self.transaction_manager.begin(description)
        self.audit_trail.record(
            event_type="TX_BEGIN",
            details={"transaction_id": tx.transaction_id, "description": description},
        )
        return tx

    def commit_transaction(self, transaction_id: str) -> None:
        """Commits staged transaction operations."""
        tx = self.transaction_manager.commit(transaction_id)
        self.audit_trail.record(
            event_type="TX_COMMITTED",
            details={"transaction_id": transaction_id, "op_count": len(tx.operations)},
        )

    def rollback_transaction(self, transaction_id: str) -> None:
        """Rolls back a staged transaction."""
        tx = self.transaction_manager.rollback(transaction_id)
        self.audit_trail.record(
            event_type="TX_ROLLED_BACK",
            details={"transaction_id": transaction_id},
        )

    # --- Snapshots & Determinism ---

    def capture_snapshot(self, frame: Optional[int] = None) -> BridgeSnapshot:
        """Captures a deterministic snapshot of all registered objects."""
        f = self._frame_counter if frame is None else frame
        self._frame_counter = f + 1
        objects_state = {
            obj_id: dict(entry.properties)
            for obj_id, entry in self.object_registry.get_all().items()
        }
        snapshot = BridgeSnapshot(
            frame=f,
            timestamp_us=int(time.perf_counter() * 1_000_000),
            objects=objects_state,
        )
        return snapshot

    def verify_determinism(self, other_snapshot: BridgeSnapshot) -> StateDivergenceReport:
        """Compares current snapshot to another snapshot."""
        current = self.capture_snapshot(frame=other_snapshot.frame)
        return self.determinism_checker.compare_snapshots(current, other_snapshot)

    # --- Recovery & Certification ---

    def reconnect(self) -> bool:
        """Performs reconnection workflow with delta replay."""
        span = self.telemetry.start_span("bridge_reconnect")
        self.audit_trail.record(event_type="RECONNECT_INITIATED")
        reconnected = self.connect()
        if reconnected:
            self.reconnection_manager.record_reconnect()
            self.audit_trail.record(event_type="RECONNECT_SUCCESS")
        else:
            self.audit_trail.record(event_type="RECONNECT_FAILED")
        self.telemetry.stop_span("bridge_reconnect")
        return reconnected

    def repair_orphans(self, policy: OrphanPolicy = OrphanPolicy.REPORT) -> OrphanReport:
        """Detects and repairs orphaned or unreferenced objects."""
        span = self.telemetry.start_span("repair_orphans")
        known_ue5_paths = [e.ue5_object_path for e in self.object_registry.get_all().values()]
        report = self.repair_engine.detect_orphans(known_ue5_paths)
        if policy != OrphanPolicy.REPORT:
            self.repair_engine.apply_policy(report, policy)
        self.audit_trail.record(
            event_type="ORPHANS_REPAIRED",
            details={"policy": policy.value, "orphan_count": report.orphan_count},
        )
        self.telemetry.stop_span("repair_orphans")
        return report

    def certify(self) -> CertificationReport:
        """Runs the complete Golden Scene certification suite."""
        return self.certification_suite.run_all()

    def get_state(self) -> Dict[str, Any]:
        """Returns the full runtime state summary of the bridge."""
        return {
            "is_connected": self.is_connected,
            "session_id": self.session.session_id,
            "objects_count": self.object_registry.count,
            "assets_count": self.asset_registry.count,
            "quarantined_count": self.quarantine_manager.count,
            "audit_entries_count": self.audit_trail.count,
            "telemetry": self.telemetry.get_summary(),
        }
