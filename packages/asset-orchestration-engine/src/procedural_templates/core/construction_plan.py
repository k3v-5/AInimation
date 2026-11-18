from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ConstructionOperation:
    operation_id: str
    type: str # CREATE_COMPONENT, SET_DIMENSIONS, ASSIGN_MATERIAL, PARENT, ASSEMBLE
    target_component: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ConstructionPlan:
    plan_id: str
    template_id: str
    template_version: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    components: List[str] = field(default_factory=list)
    operations: List[ConstructionOperation] = field(default_factory=list)
    seed: int = 42
    estimated_objects: int = 4
    estimated_polycount: int = 800
