import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from .provenance import AttributeProvenance

@dataclass
class DimensionValue:
    target: float # in meters
    tolerance: float = 0.0 # e.g. 0.05 for 5%
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    original_value: Optional[float] = None
    original_unit: Optional[str] = None
    provenance: AttributeProvenance = AttributeProvenance.EXPLICIT
    is_hard_constraint: bool = False

@dataclass
class ComponentSpecEntry:
    component_id: str
    semantic_role: str # blade, guard, grip, pommel
    required: bool = True
    dimensions: Dict[str, DimensionValue] = field(default_factory=dict)
    materials: Dict[str, Any] = field(default_factory=dict)
    provenance: AttributeProvenance = AttributeProvenance.EXPLICIT

@dataclass
class ConstraintEntry:
    constraint_id: str
    target: str
    property_name: str
    operator: str # EQUALS, FORBIDDEN, AT_LEAST, AT_MOST, RATIO_EQUALS
    value: Any
    is_hard: bool = True
    provenance: AttributeProvenance = AttributeProvenance.EXPLICIT

@dataclass
class StyleSpecEntry:
    category: str = "MEDIEVAL"
    realism: str = "STYLIZED" # REALISTIC, SEMI_REALISTIC, STYLIZED, CARTOON
    exaggeration: float = 0.0
    provenance: AttributeProvenance = AttributeProvenance.EXPLICIT

@dataclass
class AssetSpec:
    spec_id: str
    version: int = 1
    asset_type: str = "SWORD"
    asset_type_confidence: float = 1.0
    semantic_description: str = ""
    original_user_request: str = ""
    style: StyleSpecEntry = field(default_factory=StyleSpecEntry)
    components: Dict[str, ComponentSpecEntry] = field(default_factory=dict)
    dimensions: Dict[str, DimensionValue] = field(default_factory=dict)
    proportions: Dict[str, float] = field(default_factory=dict) # e.g. blade_to_handle_ratio
    constraints: List[ConstraintEntry] = field(default_factory=list)
    negative_constraints: List[str] = field(default_factory=list) # e.g. ['engraving', 'fire_fx']
    is_locked: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "AssetSpec":
        data = json.loads(json_str)
        # Parse nested dataclasses
        style_data = data.get("style", {})
        style_entry = StyleSpecEntry(
            category=style_data.get("category", "MEDIEVAL"),
            realism=style_data.get("realism", "STYLIZED"),
            exaggeration=style_data.get("exaggeration", 0.0),
            provenance=AttributeProvenance(style_data.get("provenance", "EXPLICIT"))
        )
        
        comps = {}
        for c_id, c_val in data.get("components", {}).items():
            dims = {}
            for d_k, d_v in c_val.get("dimensions", {}).items():
                dims[d_k] = DimensionValue(
                    target=d_v["target"],
                    tolerance=d_v.get("tolerance", 0.0),
                    min_value=d_v.get("min_value"),
                    max_value=d_v.get("max_value"),
                    original_value=d_v.get("original_value"),
                    original_unit=d_v.get("original_unit"),
                    provenance=AttributeProvenance(d_v.get("provenance", "EXPLICIT")),
                    is_hard_constraint=d_v.get("is_hard_constraint", False)
                )
            comps[c_id] = ComponentSpecEntry(
                component_id=c_val["component_id"],
                semantic_role=c_val["semantic_role"],
                required=c_val.get("required", True),
                dimensions=dims,
                materials=c_val.get("materials", {}),
                provenance=AttributeProvenance(c_val.get("provenance", "EXPLICIT"))
            )

        spec = cls(
            spec_id=data["spec_id"],
            version=data.get("version", 1),
            asset_type=data.get("asset_type", "SWORD"),
            asset_type_confidence=data.get("asset_type_confidence", 1.0),
            semantic_description=data.get("semantic_description", ""),
            original_user_request=data.get("original_user_request", ""),
            style=style_entry,
            components=comps,
            proportions=data.get("proportions", {}),
            negative_constraints=data.get("negative_constraints", []),
            is_locked=data.get("is_locked", False)
        )
        return spec
