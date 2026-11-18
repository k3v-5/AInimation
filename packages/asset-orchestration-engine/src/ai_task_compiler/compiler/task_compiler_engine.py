import time
from typing import Dict, Any, List, Optional
from ..core.task_types import AITaskType, ModificationScope
from ..core.task_schema import (
    AITask, ScopeBoundary, TaskRequirement, TaskExecutionPlan
)

class AITaskCompilerEngine:
    """
    AI Task Compiler Engine (AOE v34):
    Transforma intenciones humanas imprecisas en tareas con fronteras de modificación explícitas.
    """
    @staticmethod
    def compile_intent_to_task(prompt: str, target_id: str = "HOUSE_001") -> AITask:
        p_lower = prompt.lower()
        task_id = f"TASK_{int(time.time()*1000)}"

        # 1. Caso: Envejecer / Weathering
        if "vieja" in p_lower or "aged" in p_lower or "envejecer" in p_lower or "desgaste" in p_lower:
            task_type = AITaskType.AGE_ASSET
            allowed = [
                ModificationScope.SURFACE_MATERIAL,
                ModificationScope.SURFACE_DAMAGE,
                ModificationScope.COLOR_PALETTE,
                ModificationScope.DECORATIVE_DEFORMATION
            ]
            forbidden = [
                ModificationScope.FOOTPRINT,
                ModificationScope.ROOF_GEOMETRY,
                ModificationScope.DOORS,
                ModificationScope.WINDOWS
            ]
            reqs = [
                TaskRequirement("REQ_AGE_01", "Apply wood weathering and cracks"),
                TaskRequirement("REQ_AGE_02", "Add stone moss and roughness variation"),
                TaskRequirement("REQ_AGE_03", "Preserve structural footprint and dimensions", is_hard=True)
            ]
            params = {"weathering_intensity": 0.75, "damage_level": "MODERATE"}

        # 2. Caso: Redimensionar Puerta
        elif "puerta" in p_lower and ("ancha" in p_lower or "width" in p_lower or "redimensionar" in p_lower):
            task_type = AITaskType.RESIZE_COMPONENT
            allowed = [ModificationScope.DOORS, ModificationScope.NAVIGATION_MESH]
            forbidden = [
                ModificationScope.ROOF_GEOMETRY,
                ModificationScope.FOOTPRINT,
                ModificationScope.WINDOWS
            ]
            reqs = [
                TaskRequirement("REQ_DOOR_01", "Increase door width to requested dimension"),
                TaskRequirement("REQ_DOOR_02", "Ensure player navigation clearance", is_hard=True)
            ]
            params = {"component": "DOOR", "width_delta": 0.20}

        # 3. Caso por defecto: Modificar Estilo
        else:
            task_type = AITaskType.MODIFY_STYLE
            allowed = [ModificationScope.SURFACE_MATERIAL, ModificationScope.COLOR_PALETTE]
            forbidden = [ModificationScope.FOOTPRINT, ModificationScope.NAVIGATION_MESH]
            reqs = [TaskRequirement("REQ_STYLE_01", "Update visual appearance to match requested style")]
            params = {}

        return AITask(
            task_id=task_id,
            task_type=task_type,
            target_id=target_id,
            requirements=reqs,
            scope_boundary=ScopeBoundary(allowed_scopes=allowed, forbidden_scopes=forbidden),
            parameters=params
        )

    @staticmethod
    def generate_execution_plan(task: AITask) -> TaskExecutionPlan:
        ops = []
        for scope in task.scope_boundary.allowed_scopes:
            ops.append(f"EXECUTE_MODIFICATION on scope '{scope.value}' for target '{task.target_id}'")

        return TaskExecutionPlan(
            plan_id=f"PLAN_{task.task_id}",
            task=task,
            operations=ops,
            validated=True
        )
