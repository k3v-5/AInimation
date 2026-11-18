from typing import List
from ..core.task_types import ModificationScope, EnforcementAction
from ..core.task_schema import AITask, TaskValidationResult

class ScopeFirewall:
    """
    Scope Firewall (AOE v34):
    Valida que las operaciones propuestas por la IA permanezcan dentro de los límites
    ALLOWED y no toquen ningún ámbito FORBIDDEN.
    """
    @staticmethod
    def validate_operation_scope(task: AITask, target_scope: ModificationScope) -> TaskValidationResult:
        if target_scope in task.scope_boundary.forbidden_scopes:
            return TaskValidationResult(
                is_valid=False,
                violations=[f"SCOPE_VIOLATION: Modification to '{target_scope.value}' is FORBIDDEN for task '{task.task_type.value}'."],
                action=EnforcementAction.BLOCKED
            )

        if task.scope_boundary.allowed_scopes and target_scope not in task.scope_boundary.allowed_scopes:
            return TaskValidationResult(
                is_valid=False,
                violations=[f"SCOPE_VIOLATION: Modification to '{target_scope.value}' is outside the ALLOWED scopes for task '{task.task_type.value}'."],
                action=EnforcementAction.BLOCKED
            )

        return TaskValidationResult(is_valid=True, action=EnforcementAction.PERMITTED)
