from typing import List, Tuple, Optional, Dict
from ..scene.actor_registry import UnrealActor, ActorRegistry

class UnrealDependencyGraph:
    @staticmethod
    def check_safe_delete(actor_id: str, registry: ActorRegistry) -> Tuple[bool, Optional[str], List[str]]:
        """
        Comprueba si un actor puede ser eliminado sin romper dependientes (hijos, attachments).
        Devuelve (safe, error_msg, list_of_dependents).
        """
        children = registry.find_by_parent(actor_id)
        if children:
            child_ids = [c.actor_id for c in children]
            return False, f"DEPENDENCY_CONFLICT: Cannot delete actor '{actor_id}' because actors {child_ids} are attached to it.", child_ids
        return True, None, []
