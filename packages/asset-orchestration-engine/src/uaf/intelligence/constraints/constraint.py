"""
Constraint models and categories for UAF asset specifications.
UAF-81.1 Sections 10, 11, 12.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable


class ConstraintCategory(str, Enum):
    DIMENSIONAL = "DIMENSIONAL"
    GEOMETRIC = "GEOMETRIC"
    TOPOLOGICAL = "TOPOLOGICAL"
    MATERIAL = "MATERIAL"
    TEXTURE = "TEXTURE"
    PERFORMANCE = "PERFORMANCE"
    ENGINE = "ENGINE"
    GAMEPLAY = "GAMEPLAY"
    STYLE = "STYLE"
    COMPATIBILITY = "COMPATIBILITY"


class ConstraintType(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"
    PREFERRED = "PREFERRED"
    INFORMATIONAL = "INFORMATIONAL"


@dataclass(frozen=True)
class AssetConstraint:
    """
    Formal constraint applied to asset generation.
    """
    constraint_id: str
    category: ConstraintCategory
    constraint_type: ConstraintType
    target_parameter: str
    condition: str  # e.g., "max_value", "min_value", "allowed_values", "custom"
    expected_value: Any
    priority: int = 100
    description: str = ""

    def evaluate(self, actual_value: Any) -> bool:
        """Evaluates whether actual_value satisfies this constraint."""
        if actual_value is None:
            return self.constraint_type != ConstraintType.HARD

        if self.condition == "max_value":
            return actual_value <= self.expected_value
        elif self.condition == "min_value":
            return actual_value >= self.expected_value
        elif self.condition == "exact":
            return actual_value == self.expected_value
        elif self.condition == "one_of":
            return actual_value in self.expected_value
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "category": self.category.value,
            "constraint_type": self.constraint_type.value,
            "target_parameter": self.target_parameter,
            "condition": self.condition,
            "expected_value": self.expected_value,
            "priority": self.priority,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetConstraint":
        return cls(
            constraint_id=data["constraint_id"],
            category=ConstraintCategory(data["category"]),
            constraint_type=ConstraintType(data["constraint_type"]),
            target_parameter=data["target_parameter"],
            condition=data["condition"],
            expected_value=data["expected_value"],
            priority=int(data.get("priority", 100)),
            description=data.get("description", ""),
        )
