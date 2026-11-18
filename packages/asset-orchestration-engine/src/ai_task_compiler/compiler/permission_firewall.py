from typing import List, Set
from ..core.task_types import TaskPermissionType, TaskRiskLevel, SemanticOperation, TaskAction
from ..core.task_schema import TaskEnvelope

class ToolFirewall:
    """
    Tool Firewall & Prompt Injection Defense (AOE v34):
    Valida permisos granulares antes de pasar tareas al Planner e impide que inyecciones de prompt
    en datos de referencia eleven privilegios.
    """
    @staticmethod
    def sanitize_instruction(raw_prompt: str) -> str:
        # Prompt injection protection: Si el texto contiene frases de elevación de privilegios,
        # se desactiva cualquier interpretación de comando de sistema y se trata como dato puro.
        lower = raw_prompt.lower()
        if "ignora las restricciones" in lower or "ignore previous instructions" in lower or "system override" in lower:
            # Marcado como dato puro / sanitizado
            return f"[TREATED_AS_DATA] {raw_prompt}"
        return raw_prompt

    @staticmethod
    def verify_permissions(
        task: TaskEnvelope,
        granted_permissions: List[TaskPermissionType]
    ) -> bool:
        granted_set: Set[str] = {p.value for p in granted_permissions}
        for req in task.permissions:
            if req.value not in granted_set:
                raise PermissionError(
                    f"PERMISSION_DENIED: Agent lacks required permission '{req.value}' for operation '{task.requested_operation.value}'."
                )
        return True

class RiskAnalyzer:
    @staticmethod
    def assess_risk(
        operation: SemanticOperation,
        action: TaskAction,
        target_scope: str
    ) -> Tuple[TaskRiskLevel, bool]:
        """
        Calcula el nivel de riesgo y determina si requiere aprobación humana explícita.
        """
        if action == TaskAction.DELETE or operation == SemanticOperation.DELETE_ASSET:
            return TaskRiskLevel.CRITICAL, True
        if target_scope in ["LEVEL", "PROJECT"]:
            return TaskRiskLevel.HIGH, True
        if operation in [SemanticOperation.REGENERATE_ASSET, SemanticOperation.CHANGE_LAYOUT]:
            return TaskRiskLevel.MEDIUM, False
        return TaskRiskLevel.LOW, False
