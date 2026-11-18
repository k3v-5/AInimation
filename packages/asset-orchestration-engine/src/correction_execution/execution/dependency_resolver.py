from typing import List, Tuple
from ..core.correction_plan import CorrectionOperation, OperationType

class DependencyResolver:
    PRIORITY_ORDER = {
        OperationType.SET_PARENT: 1,
        OperationType.MOVE_OBJECT: 2,
        OperationType.SET_TRANSFORM: 2,
        OperationType.SET_PIVOT: 2,
        OperationType.SCALE_OBJECT: 3,
        OperationType.SET_DIMENSIONS: 3,
        OperationType.APPLY_TRANSFORM: 4,
        OperationType.MODIFY_COMPONENT: 5,
        OperationType.RECALCULATE_NORMALS: 6,
        OperationType.REGENERATE_UV: 6,
        OperationType.CHANGE_MATERIAL: 7,
        OperationType.CHANGE_BASE_COLOR: 8,
        OperationType.CHANGE_METALLIC: 8,
        OperationType.CHANGE_ROUGHNESS: 8,
        OperationType.ASSIGN_MATERIAL: 8,
        OperationType.RENAME_OBJECT: 9
    }

    @classmethod
    def resolve_order(cls, operations: List[CorrectionOperation]) -> Tuple[bool, List[CorrectionOperation], str]:
        # Ordenar por prioridad predefinida
        sorted_ops = sorted(
            operations,
            key=lambda op: cls.PRIORITY_ORDER.get(op.operation_type, 50)
        )
        return True, sorted_ops, ""
