from typing import List, Dict, Any
from .dirty_tracker import DirtyTracker
from ..components.component_registry import ComponentRegistry

class RebuildPlanner:
    def __init__(self, dirty_tracker: DirtyTracker, registry: ComponentRegistry):
        self.dirty_tracker = dirty_tracker
        self.registry = registry

    def plan_minimal_rebuild(self) -> List[str]:
        """
        Retorna la lista de componentes que necesitan reconstruirse (exclusivamente los DIRTY).
        """
        dirty_list = self.dirty_tracker.get_dirty_components()
        # Filtrar solo los componentes registrados
        return [cid for cid in dirty_list if self.registry.get(cid) is not None]
