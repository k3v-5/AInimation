from typing import Dict, Any, List
from .dependency_analyzer import DependencyAnalyzer

class ImpactAnalyzer:
    """Computes minimal regeneration boundaries and lists of invalidated artifacts/evaluations."""
    
    @classmethod
    def analyze_impact(cls, semantic_id: str, failed_component: str) -> Dict[str, Any]:
        affected_components = DependencyAnalyzer.get_dependent_components(failed_component)
        
        return {
            "semantic_id": semantic_id,
            "failed_component": failed_component,
            "affected_components": affected_components,
            "invalidated_evaluations": [f"EVAL_{semantic_id}_{comp.lower()}" for comp in affected_components],
            "required_revalidation": affected_components + [failed_component.upper()]
        }
