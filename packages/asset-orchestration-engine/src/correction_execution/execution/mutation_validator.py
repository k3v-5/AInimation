from typing import Tuple, Dict, Any, List
from ..core.object_registry import ComponentRegistry
from ..core.correction_plan import CorrectionOperation

class MutationValidator:
    @staticmethod
    def validate_preconditions(
        op: CorrectionOperation,
        component_registry: ComponentRegistry,
        protected_components: List[str] = None
    ) -> Tuple[bool, str]:
        # 1. Comprobar componentes bloqueados
        if component_registry.is_locked(op.target):
            return False, f"DENIED: Target component '{op.target}' is LOCKED and cannot be modified."

        # 2. Comprobar lista de preservación
        if protected_components and op.target in protected_components:
            return False, f"DENIED: Target component '{op.target}' is in the PROTECTED preserve list."

        return True, ""
