"""
UAF-81.99: Chaos Destruction & Physical Fracturing Core Contracts.
Pydantic v2 domain models and enums for materials, Voronoi sites, fractured pieces,
anchor fields, GeometryCollections, and Niagara debris particle presets.
"""

from enum import Enum, IntEnum
import math
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DestructionMaterialType(str, Enum):
    CONCRETE = "CONCRETE"
    MASONRY_BRICK = "MASONRY_BRICK"
    REINFORCED_METAL = "REINFORCED_METAL"
    TEMPERED_GLASS = "TEMPERED_GLASS"
    STRUCTURAL_WOOD = "STRUCTURAL_WOOD"
    COMPOSITE_PLASTIC = "COMPOSITE_PLASTIC"

    @property
    def density_kg_per_m3(self) -> float:
        densities = {
            DestructionMaterialType.CONCRETE: 2400.0,
            DestructionMaterialType.MASONRY_BRICK: 1900.0,
            DestructionMaterialType.REINFORCED_METAL: 7850.0,
            DestructionMaterialType.TEMPERED_GLASS: 2500.0,
            DestructionMaterialType.STRUCTURAL_WOOD: 650.0,
            DestructionMaterialType.COMPOSITE_PLASTIC: 1200.0,
        }
        return densities[self]


class FracturePatternType(str, Enum):
    VORONOI_UNIFORM = "VORONOI_UNIFORM"
    VORONOI_CLUSTER_RADIAL = "VORONOI_CLUSTER_RADIAL"
    PLANAR_SLICES = "PLANAR_SLICES"
    BRICK_WALL_PATTERN = "BRICK_WALL_PATTERN"


class ClusterHierarchyLevel(IntEnum):
    ROOT_WHOLE = 0
    MACRO_CHUNK = 1
    MICRO_DEBRIS = 2


class AnchorMode(str, Enum):
    BASE_GROUNDED = "BASE_GROUNDED"
    CEILING_SUSPENDED = "CEILING_SUSPENDED"
    LATERAL_PILLARS = "LATERAL_PILLARS"
    NONE_DYNAMIC = "NONE_DYNAMIC"


class Vector3D(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_ue5_cm(self) -> "Vector3D":
        return Vector3D(x=self.x * 100.0, y=self.y * 100.0, z=self.z * 100.0)

    @classmethod
    def from_ue5_cm(cls, x_cm: float, y_cm: float, z_cm: float) -> "Vector3D":
        return cls(x=x_cm * 0.01, y=y_cm * 0.01, z=z_cm * 0.01)

    def distance_to(self, other: "Vector3D") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

    def normalized(self) -> "Vector3D":
        mag = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if mag == 0:
            return Vector3D(x=0.0, y=0.0, z=1.0)
        return Vector3D(x=self.x / mag, y=self.y / mag, z=self.z / mag)

    def __add__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        return Vector3D(x=self.x * scalar, y=self.y * scalar, z=self.z * scalar)

    __rmul__ = __mul__


class BoundingBox3D(BaseModel):
    min_x: float = 0.0
    max_x: float = 1.0
    min_y: float = 0.0
    max_y: float = 1.0
    min_z: float = 0.0
    max_z: float = 1.0

    def contains(self, p: Vector3D, margin: float = 0.0) -> bool:
        return (
            (self.min_x - margin) <= p.x <= (self.max_x + margin)
            and (self.min_y - margin) <= p.y <= (self.max_y + margin)
            and (self.min_z - margin) <= p.z <= (self.max_z + margin)
        )

    def volume(self) -> float:
        dx = max(0.0, self.max_x - self.min_x)
        dy = max(0.0, self.max_y - self.min_y)
        dz = max(0.0, self.max_z - self.min_z)
        return dx * dy * dz

    def center(self) -> Vector3D:
        return Vector3D(
            x=(self.min_x + self.max_x) * 0.5,
            y=(self.min_y + self.max_y) * 0.5,
            z=(self.min_z + self.max_z) * 0.5,
        )


class VoronoiSite(BaseModel):
    site_id: str
    position: Vector3D
    weight: float = 1.0
    cluster_id: int = 0


class FracturedPiece(BaseModel):
    piece_id: str
    parent_piece_id: Optional[str] = None
    cluster_level: ClusterHierarchyLevel = ClusterHierarchyLevel.MACRO_CHUNK
    centroid: Vector3D
    volume_m3: float = 0.01
    mass_kg: float = 24.0
    damage_threshold_joules: float = 500.0
    is_anchored: bool = False
    bounding_box: Optional[BoundingBox3D] = None
    neighbor_piece_ids: List[str] = Field(default_factory=list)
    contact_areas: Dict[str, float] = Field(default_factory=dict)


class AnchorFieldSpec(BaseModel):
    field_id: str
    anchor_mode: AnchorMode = AnchorMode.BASE_GROUNDED
    bounding_box: BoundingBox3D
    stiffness: float = 1.0


class DebrisParticlePreset(BaseModel):
    preset_name: str
    dust_color_rgba: List[float] = Field(default_factory=lambda: [0.7, 0.7, 0.7, 0.5])
    particle_spawn_rate: float = 100.0
    lifetime_s: float = 3.0
    initial_speed_min: float = 2.0
    initial_speed_max: float = 12.0
    spark_chance: float = 0.0


class GeometryCollectionSpec(BaseModel):
    collection_id: str
    base_mesh_name: str
    material_type: DestructionMaterialType = DestructionMaterialType.CONCRETE
    total_pieces: int = 0
    pieces: Dict[str, FracturedPiece] = Field(default_factory=dict)
    density_kg_m3: float = 2400.0
    macro_damage_threshold: float = 1000.0
    micro_damage_threshold: float = 300.0
    anchor_fields: List[AnchorFieldSpec] = Field(default_factory=list)


class ChaosDestructionBundle(BaseModel):
    asset_name: str
    collection_spec: GeometryCollectionSpec
    debris_preset: DebrisParticlePreset
    ue5_manifest: Dict[str, Any] = Field(default_factory=dict)
