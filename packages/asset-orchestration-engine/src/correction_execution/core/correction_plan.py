import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class OperationType(str, Enum):
    SCALE_OBJECT = "SCALE_OBJECT"
    MOVE_OBJECT = "MOVE_OBJECT"
    ROTATE_OBJECT = "ROTATE_OBJECT"
    SET_DIMENSIONS = "SET_DIMENSIONS"
    SET_TRANSFORM = "SET_TRANSFORM"
    SET_PIVOT = "SET_PIVOT"
    APPLY_TRANSFORM = "APPLY_TRANSFORM"
    CHANGE_MATERIAL = "CHANGE_MATERIAL"
    CHANGE_BASE_COLOR = "CHANGE_BASE_COLOR"
    CHANGE_METALLIC = "CHANGE_METALLIC"
    CHANGE_ROUGHNESS = "CHANGE_ROUGHNESS"
    ASSIGN_MATERIAL = "ASSIGN_MATERIAL"
    MODIFY_COMPONENT = "MODIFY_COMPONENT"
    REBUILD_COMPONENT = "REBUILD_COMPONENT"
    REPLACE_COMPONENT = "REPLACE_COMPONENT"
    DELETE_COMPONENT = "DELETE_COMPONENT"
    DUPLICATE_COMPONENT = "DUPLICATE_COMPONENT"
    RENAME_OBJECT = "RENAME_OBJECT"
    RENAME_COLLECTION = "RENAME_COLLECTION"
    SET_PARENT = "SET_PARENT"
    SET_VISIBILITY = "SET_VISIBILITY"
    SET_COLLECTION = "SET_COLLECTION"
    RECALCULATE_NORMALS = "RECALCULATE_NORMALS"
    RECALCULATE_UV = "RECALCULATE_UV"
    REGENERATE_UV = "REGENERATE_UV"
    REBUILD_COLLISION = "REBUILD_COLLISION"

@dataclass
class CorrectionOperation:
    operation_id: str
    operation_type: OperationType
    target: str # component_id or object_id
    parameters: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    source_failure: str = ""
    risk: str = "LOW" # LOW, MEDIUM, HIGH, CRITICAL
    reversible: bool = True
    dependencies: List[str] = field(default_factory=list)
    preconditions: Dict[str, Any] = field(default_factory=dict)
    postconditions: Dict[str, Any] = field(default_factory=dict)
    idempotent: bool = True

@dataclass
class CorrectionPlan:
    plan_id: str
    asset_id: str
    goal_id: str
    source_verification_id: str
    operations: List[CorrectionOperation] = field(default_factory=list)
    risk_level: str = "LOW"
    estimated_impact: str = "LOCAL"
    rollback_strategy: str = "ROLLBACK_ALL" # ROLLBACK_ALL or CONTINUE_SAFE
    expected_result: Dict[str, Any] = field(default_factory=dict)
