from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

class AssetCategory(str, Enum):
    WEAPON = "weapon"
    SHIELD = "shield"
    PROP = "prop"
    CHARACTER = "character"
    STRUCTURE = "structure"
    TOOL = "tool"

class PrimitiveType(str, Enum):
    BOX = "box"
    CYLINDER = "cylinder"
    SPHERE = "sphere"
    CAPSULE = "capsule"
    CONE = "cone"
    TORUS = "torus"
    CUSTOM = "custom"

class SymmetryType(str, Enum):
    NONE = "none"
    BILATERAL_X = "bilateral_x"
    RADIAL = "radial"

class AssetStatus(str, Enum):
    DRAFT = "DRAFT"
    BUILDING = "BUILDING"
    VALIDATING = "VALIDATING"
    VALID = "VALID"
    INVALID = "INVALID"
    FAILED = "FAILED"
    READY = "READY"

@dataclass
class DimensionsSpec:
    height: float = 1.0
    width: float = 1.0
    depth: float = 1.0
    unit: str = "meters"

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.width, self.depth, self.height)

@dataclass
class ComponentSpec:
    id: str
    type: str
    primitive: PrimitiveType = PrimitiveType.BOX
    parent_id: Optional[str] = None
    dimensions: Optional[DimensionsSpec] = None
    relative_position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    relative_rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    relative_scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    material_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StyleSpec:
    category: str = "stylized"
    symmetry: SymmetryType = SymmetryType.NONE
    tags: List[str] = field(default_factory=list)

@dataclass
class BudgetSpec:
    max_triangles: int = 10000
    max_materials: int = 4
    max_lods: int = 1
    polygon_budget: int = 5000

@dataclass
class AssetSpecification:
    asset_id: str
    name: str
    category: AssetCategory = AssetCategory.PROP
    dimensions: DimensionsSpec = field(default_factory=DimensionsSpec)
    style: StyleSpec = field(default_factory=StyleSpec)
    budget: BudgetSpec = field(default_factory=BudgetSpec)
    components: List[ComponentSpec] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    engine_target: str = "unreal"
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
