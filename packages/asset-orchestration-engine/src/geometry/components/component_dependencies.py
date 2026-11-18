from typing import Dict, Set, List

class ComponentDependencies:
    def __init__(self):
        self.hierarchy_deps: Dict[str, str] = {} # child_id -> parent_id
        self.parametric_deps: Dict[str, Set[str]] = {} # source_comp_id -> set of dependent_comp_ids

    def set_parent(self, child_id: str, parent_id: str):
        self.hierarchy_deps[child_id] = parent_id

    def add_parametric_dependency(self, source_comp_id: str, dependent_comp_id: str):
        if source_comp_id not in self.parametric_deps:
            self.parametric_deps[source_comp_id] = set()
        self.parametric_deps[source_comp_id].add(dependent_comp_id)

    def get_dependents(self, comp_id: str) -> List[str]:
        """
        Retorna todos los componentes que dependen paramétricamente de comp_id.
        """
        deps = set()
        # Buscar coincidencias por ID exacto o sufijo de nombre
        for src, targets in self.parametric_deps.items():
            if src == comp_id or comp_id.endswith(src):
                deps.update(targets)
        return list(deps)
