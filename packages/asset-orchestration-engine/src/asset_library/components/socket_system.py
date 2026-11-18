from typing import Dict, Any, Tuple
from ..core.library_schema import ComponentDefinition

class SocketSystem:
    @staticmethod
    def validate_composition(components: Dict[str, ComponentDefinition]) -> Tuple[bool, str]:
        # Validar que exista al menos una base estructural (ej. blade + guard + handle)
        required_roles = ["blade", "guard", "handle"]
        present_roles = [c.category for c in components.values()]
        for role in required_roles:
            if role not in present_roles:
                return False, f"SOCKET_COMPOSITION_ERROR: Missing required structural role '{role}' in component assembly."
        return True, "Composition valid."
