from typing import List, Dict

class DependencyAnalyzer:
    """Analyzes cascading component dependencies to determine minimum invalidation boundary."""

    DEP_GRAPH: Dict[str, List[str]] = {
        "GEOMETRY": ["UV", "MATERIAL", "LOD", "COLLISION", "EVALUATION", "DELIVERY"],
        "TRANSFORM": ["COLLISION", "LOD", "EVALUATION"],
        "UV": ["MATERIAL", "TEXTURE", "EVALUATION"],
        "MATERIAL": ["SHADER", "EVALUATION"],
        "LOD": ["EVALUATION"],
        "COLLISION": ["EVALUATION", "UNREAL_READINESS"],
        "EVALUATION": ["GOLDEN_COMPARISON", "DELIVERY"]
    }

    @classmethod
    def get_downstream_dependencies(cls, component_type: str) -> List[str]:
        comp = component_type.upper()
        return cls.DEP_GRAPH.get(comp, ["EVALUATION"])
