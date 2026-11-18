from typing import Dict, Any, List, Optional
from ..core.task_types import (
    TaskSource, TaskAction, SemanticOperation, TaskScope, TaskPriority,
    TaskRiskLevel, TaskStatusEnum, AmbiguityType, TaskPermissionType, ConstraintTypeEnum
)
from ..core.task_schema import (
    TargetSpec, TaskConstraint, TaskPreference, TaskEnvelope, TaskPreview,
    TaskDecomposition, TaskResult
)
from ..compiler.task_compiler import TaskCompiler
from ..compiler.task_decomposer import TaskDecomposer
from ..compiler.permission_firewall import ToolFirewall
from ..compiler.unit_normalizer import TaskUnitNormalizer

class AITaskCompilerAPI:
    """
    AI Task Compiler API (AOE v34)
    
    Frontera obligatoria entre Antigravity / Agentes de IA y el Motor Determinista.
    La IA nunca envía instrucciones directas a Blender ni al MCP.
    Pasa siempre por este compilador que extrae intenciones, objetivos, restricciones negativas,
    resuelve referencias, normaliza unidades y genera un TaskEnvelope estructurado.
    """
    @staticmethod
    def compile_task(
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        source: TaskSource = TaskSource.USER
    ) -> TaskEnvelope:
        return TaskCompiler.compile_instruction(instruction, context, source)

    @staticmethod
    def preview_task(envelope: TaskEnvelope) -> TaskPreview:
        return TaskCompiler.preview_task(envelope)

    @staticmethod
    def decompose_task(instruction: str, target_id: str = "HOUSE_001") -> TaskDecomposition:
        return TaskDecomposer.decompose_compound_task(instruction, target_id)

    @staticmethod
    def verify_permissions(
        envelope: TaskEnvelope,
        granted_permissions: List[TaskPermissionType]
    ) -> bool:
        return ToolFirewall.verify_permissions(envelope, granted_permissions)

    @staticmethod
    def normalize_unit(val_str: str) -> Dict[str, Any]:
        return TaskUnitNormalizer.normalize_dimension(val_str)
