from typing import Dict, List, Set

class DependencyAnalyzer:
    """Analyzes downstream dependencies of components to determine necessary re-validations."""
    
    DEPENDENCY_GRAPH: Dict[str, List[str]] = {
        "GEOMETRY": ["UV", "MATERIAL", "LOD", "COLLISION", "EVALUATION", "GOLDEN", "PACKAGE"],
        "UV": ["MATERIAL", "EVALUATION", "GOLDEN", "PACKAGE"],
        "MATERIAL": ["EVALUATION", "GOLDEN", "PACKAGE"],
        "LOD": ["EVALUATION", "GOLDEN", "PACKAGE"],
        "COLLISION": ["ENGINE_READINESS", "EVALUATION", "PACKAGE"],
        "TRANSFORM": ["COLLISION", "ENGINE_READINESS", "EVALUATION", "PACKAGE"],
        "AXIS": ["ENGINE_READINESS", "EVALUATION", "PACKAGE"]
    }

    @classmethod
    def get_dependent_components(cls, component: str) -> List[str]:
        comp_clean = component.upper()
        deps: Set[str] = set()
        queue = [comp_clean]

        while queue:
            curr = queue.pop(0)
            direct_deps = cls.DEPENDENCY_GRAPH.get(curr, [])
            for d in direct_deps:
                if d not in deps:
                    deps.add(d)
                    queue.append(d)

        return sorted(list(deps))
