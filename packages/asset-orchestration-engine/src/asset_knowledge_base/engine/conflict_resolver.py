from typing import Dict, Any, List, Optional
from ..core.knowledge_types import ConflictPriority

class ConflictResolver:
    """
    Jerarquía Estricta de Resolución de Conflictos:
    SAFETY > PLATFORM > PROJECT > ASSET > STYLE > PREFERENCE
    """
    PRIORITY_ORDER = [
        ConflictPriority.SAFETY,
        ConflictPriority.PLATFORM,
        ConflictPriority.PROJECT,
        ConflictPriority.ASSET,
        ConflictPriority.STYLE,
        ConflictPriority.PREFERENCE
    ]

    @classmethod
    def resolve_parameter_conflict(
        cls,
        param_name: str,
        proposals: Dict[ConflictPriority, Any]
    ) -> Dict[str, Any]:
        for priority in cls.PRIORITY_ORDER:
            if priority in proposals:
                return {
                    "parameter": param_name,
                    "winning_value": proposals[priority],
                    "resolved_by_priority": priority.value,
                    "suppressed_proposals": {p.value: v for p, v in proposals.items() if p != priority}
                }
        raise ValueError(f"No proposals provided for parameter '{param_name}'.")
