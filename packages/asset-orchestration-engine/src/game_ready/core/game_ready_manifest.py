from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ..lod.lod_generator import GeneratedLODLevel
from ..collision.collision_generator import CollisionHull
from ..sockets.socket_schema import SocketDefinition
from ..unreal.asset_mapper import UnrealAssetMapping
from ..unreal.import_settings import UnrealImportSettings

@dataclass
class GameReadyManifest:
    asset_id: str
    source_geometry_version: str
    source_appearance_version: str
    game_ready_version: str = "v1"
    status: str = "GAME_READY"
    unreal_mapping: Optional[UnrealAssetMapping] = None
    import_settings: Optional[UnrealImportSettings] = None
    lods_summary: Dict[str, int] = field(default_factory=dict) # LOD0: tris, LOD1: tris
    collision_hulls: List[str] = field(default_factory=list)
    sockets: List[str] = field(default_factory=list)
    material_slots: List[str] = field(default_factory=list)
    dimensions_cm: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    validation_status: str = "APPROVED"
