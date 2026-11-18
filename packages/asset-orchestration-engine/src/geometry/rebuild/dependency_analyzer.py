from typing import List, Set
from ..components.component_dependencies import ComponentDependencies
from .dirty_tracker import DirtyTracker

class DependencyAnalyzer:
    def __init__(self, dependencies: ComponentDependencies, dirty_tracker: DirtyTracker):
        self.dependencies = dependencies
        self.dirty_tracker = dirty_tracker

    def propagate_dirty(self, changed_component_id: str) -> List[str]:
        """
        Marca como DIRTY el componente modificado y propaga recursivamente
        ÚNICAMENTE a sus componentes dependientes. Retorna la lista de componentes dirty.
        """
        dirty_set: Set[str] = set()
        queue = [changed_component_id]

        while queue:
            current = queue.pop(0)
            if current not in dirty_set:
                dirty_set.add(current)
                self.dirty_tracker.mark_dirty(current)
                # Buscar dependientes directos
                dependents = self.dependencies.get_dependents(current)
                for dep in dependents:
                    if dep not in dirty_set:
                        queue.append(dep)

        return list(dirty_set)
