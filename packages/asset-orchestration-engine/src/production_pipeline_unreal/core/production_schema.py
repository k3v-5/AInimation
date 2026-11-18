import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .production_types import (
    AssetLifecycle, PivotType, CollisionStrategy,
    NanitePolicy, ChangeClass, QualityGateStatus, SourceOwnership
)

@dataclass
class SocketDefinition:
    socket_name: str
    relative_location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    relative_rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    purpose: str = "ATTACHMENT"
    is_critical: bool = False

@dataclass
class BlenderExportContract:
    units: str = "CENTIMETERS"
    coordinate_forward: str = "-Y"
    coordinate_up: str = "+Z"
    pivot_type: PivotType = PivotType.BASE
    apply_transforms: bool = True
    validate_manifold: bool = True

@dataclass
class CollisionContract:
    strategy: CollisionStrategy = CollisionStrategy.AUTO_CONVEX
    ucx_name: str = "UCX_Asset"
    hull_count: int = 1
    is_convex: bool = True

@dataclass
class LODContract:
    lod_count: int = 4
    lod_reduction_ratios: List[float] = field(default_factory=lambda: [1.0, 0.50, 0.25, 0.12])
    screen_sizes: List[float] = field(default_factory=lambda: [1.0, 0.60, 0.30, 0.10])

@dataclass
class ExportManifest:
    asset_id: str
    version: str = "1.0.0"
    mesh_name: str = "SM_Asset"
    material_instances: List[str] = field(default_factory=list)
    textures: List[str] = field(default_factory=list)
    collision_name: str = "UCX_Asset"
    lod_count: int = 4
    sockets: List[SocketDefinition] = field(default_factory=list)
    content_hash: str = ""
    pipeline_fingerprint: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProductionAsset:
    asset_id: str
    version: str = "1.0.0"
    status: AssetLifecycle = AssetLifecycle.DRAFT
    unreal_path: str = "/Game/Published/Environment/"
    manifest: Optional[ExportManifest] = None
    ownership: SourceOwnership = SourceOwnership.AI
    is_manual_modified: bool = False

@dataclass
class QualityGateReport:
    asset_id: str
    status: QualityGateStatus
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class PublicationRecord:
    publication_id: str
    asset_id: str
    version: str
    target_path: str
    previous_version: Optional[str] = None
    status: str = "COMMITTED"
    timestamp: float = field(default_factory=time.time)
