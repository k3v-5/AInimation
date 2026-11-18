from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class ScopeSpec:
    asset_ids: Optional[List[str]] = None
    allowed_components: Optional[List[str]] = None
    allow_new_components: bool = False
    allow_delete: bool = False

class ScopeManager:
    @staticmethod
    def validate_action(
        scope: Optional[ScopeSpec],
        asset_id: str,
        target_component_id: Optional[str] = None,
        is_delete_op: bool = False,
        is_new_comp_op: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Devuelve (es_valido, error_code, error_message)
        """
        if not scope:
            return True, None, None

        # 1. Validar asset_id
        if scope.asset_ids and asset_id not in scope.asset_ids:
            return False, "SCOPE_VIOLATION", f"Asset '{asset_id}' is outside permitted scope {scope.asset_ids}."

        # 2. Validar allowed_components
        if scope.allowed_components and target_component_id:
            # Comprobar id directo o sufijo
            comp_name = target_component_id.split(".")[-1]
            if target_component_id not in scope.allowed_components and comp_name not in scope.allowed_components:
                return False, "SCOPE_VIOLATION", f"Component '{target_component_id}' is not in allowed components scope {scope.allowed_components}."

        # 3. Validar operaciones destructivas
        if is_delete_op and not scope.allow_delete:
            return False, "OPERATION_NOT_ALLOWED", "Destructive operation (delete) is prohibited by current task scope."

        # 4. Validar creación de nuevos componentes
        if is_new_comp_op and not scope.allow_new_components:
            return False, "OPERATION_NOT_ALLOWED", "Creating new components is prohibited by current task scope."

        return True, None, None
