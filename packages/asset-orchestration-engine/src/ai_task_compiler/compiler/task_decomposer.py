import time
from typing import List, Dict
from ..core.task_types import (
    TaskSource, TaskAction, SemanticOperation, TaskPriority, TaskRiskLevel, TaskStatusEnum
)
from ..core.task_schema import TaskEnvelope, TargetSpec, TaskDecomposition

class TaskDecomposer:
    @staticmethod
    def decompose_compound_task(parent_prompt: str, target_id: str = "HOUSE_001") -> TaskDecomposition:
        p_id = f"TASK_{int(time.time()*1000)}"
        t1_id = f"{p_id}_01_STRUCTURE"
        t2_id = f"{p_id}_02_MATERIALS"
        t3_id = f"{p_id}_03_DAMAGE"
        t4_id = f"{p_id}_04_FOLIAGE"
        t5_id = f"{p_id}_05_VALIDATION"

        subtasks = [
            TaskEnvelope(
                task_id=t1_id,
                requested_operation=SemanticOperation.CHANGE_STRUCTURE if hasattr(SemanticOperation, 'CHANGE_STRUCTURE') else SemanticOperation.CHANGE_DIMENSIONS,
                target=TargetSpec(target_id, target_id),
                parameters={"operation": "STRUCTURE_SETUP"}
            ),
            TaskEnvelope(
                task_id=t2_id,
                requested_operation=SemanticOperation.CHANGE_MATERIAL,
                target=TargetSpec(target_id, target_id),
                parameters={"weathering": 0.85, "palette": "AGED_DARK"}
            ),
            TaskEnvelope(
                task_id=t3_id,
                requested_operation=SemanticOperation.AGE_ASSET,
                target=TargetSpec(target_id, target_id),
                parameters={"damage_level": "HEAVY", "cracks": True}
            ),
            TaskEnvelope(
                task_id=t4_id,
                requested_operation=SemanticOperation.ADD_COMPONENT,
                target=TargetSpec(f"{target_id}.FOLIAGE", target_id),
                parameters={"component": "VINES_AND_MOSS"}
            ),
            TaskEnvelope(
                task_id=t5_id,
                requested_operation=SemanticOperation.FIX_COLLISION,
                target=TargetSpec(target_id, target_id),
                parameters={"validation_pass": True}
            )
        ]

        deps = {
            t1_id: [],
            t2_id: [t1_id],
            t3_id: [t2_id],
            t4_id: [t1_id],
            t5_id: [t3_id, t4_id]
        }

        return TaskDecomposition(
            parent_task_id=p_id,
            subtasks=subtasks,
            dependency_graph=deps
        )
