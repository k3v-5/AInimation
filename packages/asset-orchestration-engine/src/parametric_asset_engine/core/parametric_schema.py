import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .parametric_types import (
    ParamType, UnitType, RoofType, ComponentState, PivotType,
    GenerationStrategy, ParametricErrorType
)

@dataclass
class ParamDefinition:
    name: str
    type: ParamType
    unit: UnitType = UnitType.METERS
    default: Any = 0.0
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    editable: bool = True
    affects: List[str] = field(default_factory=list)

@dataclass
class ResolvedParameters:
    values: Dict[str, Any] = field(default_factory=dict)
    parameter_hash: str = ""

@dataclass
class GeneratedComponent:
    component_id: str
    object_ids: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    materials: Dict[str, str] = field(default_factory=dict)
    state: ComponentState = ComponentState.VALID
    triangles: int = 100
    bounds: Dict[str, float] = field(default_factory=dict)

@dataclass
class AssetSnapshot:
    snapshot_id: str
    asset_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    components: Dict[str, GeneratedComponent] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class AssetDefinition:
    asset_id: str
    category: str = "MEDIEVAL_HOUSE"
    parameters: Dict[str, Any] = field(default_factory=dict)
    components: Dict[str, GeneratedComponent] = field(default_factory=dict)
    generation_seed: int = 42
    strategy: GenerationStrategy = GenerationStrategy.PARAMETRIC
