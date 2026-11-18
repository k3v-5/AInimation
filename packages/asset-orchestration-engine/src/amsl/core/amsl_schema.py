import copy
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .amsl_types import (
    AMSLAssetType, AMSLAssetPurpose, DimensionMode, RelationshipType,
    StyleFamily, DetailLevel, MaterialCategory, DamageLevel, CollisionType,
    QualityLevel, RebuildPolicy, ConstraintType, ConstraintPriority, ValidationCategory
)

@dataclass
class CoordinateSystem:
    units: str = "m"
    up_axis: str = "Z"
    forward_axis: "str" = "Y"
    handedness: str = "RIGHT"

@dataclass
class DimensionValue:
    target: float
    unit: str = "m"
    tolerance: float = 0.05
    mode: DimensionMode = DimensionMode.ABSOLUTE
    min_val: Optional[float] = None
    max_val: Optional[float] = None

@dataclass
class DimensionsSpec:
    width: Optional[DimensionValue] = None
    depth: Optional[DimensionValue] = None
    height: Optional[DimensionValue] = None
    length: Optional[DimensionValue] = None
    diameter: Optional[DimensionValue] = None
    thickness: Optional[DimensionValue] = None
    proportions: Dict[str, float] = field(default_factory=dict)
    expected_bounds: Dict[str, float] = field(default_factory=dict)

@dataclass
class StructureSpec:
    floors: int = 1
    foundation: bool = True
    roof: Dict[str, Any] = field(default_factory=lambda: {"type": "GABLE", "pitch": 40.0})
    entrance: str = "front"

@dataclass
class ComponentSpec:
    id: str
    type: str
    count: int = 1
    side: str = "north"
    position: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RelationshipSpec:
    relation_type: RelationshipType
    source_component_id: str
    target_component_id: str

@dataclass
class StyleSpec:
    era: StyleFamily = StyleFamily.MEDIEVAL
    language: str = "RUSTIC"
    realism: str = "REALISTIC"
    weight: float = 1.0
    silhouette: Dict[str, Any] = field(default_factory=lambda: {"shape": "rectangular", "roof_profile": "gable"})
    wear_level: float = 0.0

@dataclass
class GeometrySpec:
    topology: str = "MANIFOLD_QUADS"
    polygon_budget: int = 15000
    detail_level: DetailLevel = DetailLevel.HIGH
    detail_distribution: Dict[str, float] = field(default_factory=lambda: {"primary": 0.6, "secondary": 0.3, "tertiary": 0.1})

@dataclass
class MaterialSpec:
    material_id: str
    category: MaterialCategory
    base_color: str = "#8B4513"
    roughness: float = 0.8
    metallic: float = 0.0
    wear: float = 0.0

@dataclass
class DamageSpec:
    level: DamageLevel = DamageLevel.NONE
    cracks: bool = False
    dents: bool = False
    preserve_structural_integrity: bool = True

@dataclass
class CollisionSpec:
    collision_required: bool = True
    collision_type: CollisionType = CollisionType.BOX
    walkable: bool = True
    blocking: bool = True

@dataclass
class GameplaySpec:
    interactable: bool = False
    destructible: bool = False
    climbable: bool = False
    cover: bool = False
    spawn_point: bool = False

@dataclass
class ReferenceSpec:
    id: str
    type: str = "IMAGE"
    priority: str = "HIGH"
    applies_to: List[str] = field(default_factory=list)
    source_path: str = ""

@dataclass
class ConstraintSpec:
    type: ConstraintType = ConstraintType.HARD
    priority: ConstraintPriority = ConstraintPriority.USER_HARD
    rule: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationSpec:
    generator: str = "ProceduralAssetBuilder"
    generator_version: str = "1.0.0"
    seed: int = 42191
    deterministic: bool = True
    rebuild_policy: RebuildPolicy = RebuildPolicy.DEPENDENCIES

@dataclass
class ValidationSpec:
    categories: List[ValidationCategory] = field(
        default_factory=lambda: [
            ValidationCategory.STRUCTURAL,
            ValidationCategory.DIMENSIONAL,
            ValidationCategory.GEOMETRIC
        ]
    )

@dataclass
class QualityProfileSpec:
    profile: QualityLevel = QualityLevel.HIGH
    target_engine: str = "UNREAL"
    target_platform: str = "PC"

@dataclass
class ProvenanceSpec:
    source_prompt: str = ""
    source_task: str = ""
    creator_agent: str = "antigravity"
    generation_date: float = field(default_factory=time.time)

@dataclass
class AssetSpecification:
    specification_id: str = "SPEC_2026_000001"
    schema_version: str = "1.0.0"
    asset_id: str = "HOUSE_001"
    semantic_id: str = "LEVEL_01.VILLAGE.HOUSE_001"
    asset_type: AMSLAssetType = AMSLAssetType.BUILDING
    category: str = "MEDIEVAL_HOUSE"
    purpose: AMSLAssetPurpose = AMSLAssetPurpose.ENVIRONMENT
    coordinates: CoordinateSystem = field(default_factory=CoordinateSystem)
    dimensions: DimensionsSpec = field(default_factory=DimensionsSpec)
    structure: StructureSpec = field(default_factory=StructureSpec)
    components: List[ComponentSpec] = field(default_factory=list)
    relationships: List[RelationshipSpec] = field(default_factory=list)
    style: StyleSpec = field(default_factory=StyleSpec)
    geometry: GeometrySpec = field(default_factory=GeometrySpec)
    materials: List[MaterialSpec] = field(default_factory=list)
    damage: DamageSpec = field(default_factory=DamageSpec)
    collision: CollisionSpec = field(default_factory=CollisionSpec)
    gameplay: GameplaySpec = field(default_factory=GameplaySpec)
    references: List[ReferenceSpec] = field(default_factory=list)
    constraints: List[ConstraintSpec] = field(default_factory=list)
    generation: GenerationSpec = field(default_factory=GenerationSpec)
    validation: ValidationSpec = field(default_factory=ValidationSpec)
    quality: QualityProfileSpec = field(default_factory=QualityProfileSpec)
    provenance: ProvenanceSpec = field(default_factory=ProvenanceSpec)
    tags: List[str] = field(default_factory=lambda: ["medieval", "house", "procedural"])
    metadata: Dict[str, Any] = field(default_factory=dict)
    extensions: Dict[str, Any] = field(default_factory=dict)

    def to_canonical_dict(self) -> Dict[str, Any]:
        """Serialización canónica para hashing y comparaciones deterministas."""
        dim_dict = {}
        if self.dimensions.width:
            dim_dict["width"] = {"val": self.dimensions.width.target, "unit": self.dimensions.width.unit}
        if self.dimensions.depth:
            dim_dict["depth"] = {"val": self.dimensions.depth.target, "unit": self.dimensions.depth.unit}
        if self.dimensions.height:
            dim_dict["height"] = {"val": self.dimensions.height.target, "unit": self.dimensions.height.unit}

        comps = sorted(
            [{"id": c.id, "type": c.type, "count": c.count, "params": c.parameters} for c in self.components],
            key=lambda x: x["id"]
        )
        mats = sorted(
            [{"id": m.material_id, "cat": m.category.value, "col": m.base_color, "r": m.roughness} for m in self.materials],
            key=lambda x: x["id"]
        )

        return {
            "schema_version": self.schema_version,
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "category": self.category,
            "dimensions": dim_dict,
            "structure": {
                "floors": self.structure.floors,
                "roof": self.structure.roof
            },
            "components": comps,
            "style": {
                "era": self.style.era.value,
                "language": self.style.language,
                "realism": self.style.realism
            },
            "materials": mats,
            "generation": {
                "seed": self.generation.seed,
                "deterministic": self.generation.deterministic,
                "version": self.generation.generator_version
            }
        }

    def compute_specification_hash(self) -> str:
        canonical = self.to_canonical_dict()
        serialized = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

@dataclass
class SpecificationDiff:
    added: Dict[str, Any] = field(default_factory=dict)
    removed: Dict[str, Any] = field(default_factory=dict)
    modified: Dict[str, Any] = field(default_factory=dict)
    locked: Dict[str, Any] = field(default_factory=dict)
    unchanged: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BuildRequirements:
    required_builders: List[str] = field(default_factory=list)
    modification_cost: str = "LOW"
    requires_rebuild: bool = False
    dependencies: List[str] = field(default_factory=list)
