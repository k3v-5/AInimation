from typing import List, Dict, Any
from ..core.msp_types import StrategyRiskLevel
from ..core.msp_schema import CostEstimate, ComponentStrategy

class CostEstimator:
    @classmethod
    def estimate_cost(
        cls,
        component_strategies: List[ComponentStrategy],
        triangle_budget: int
    ) -> CostEstimate:
        num_objects = len(component_strategies)
        num_modifiers = sum(len(c.modifiers) for c in component_strategies)
        est_triangles = sum(800 + len(c.modifiers) * 300 for c in component_strategies)

        complexity = min(round((num_objects * 0.08) + (num_modifiers * 0.05) + (est_triangles / (triangle_budget * 2.0 if triangle_budget > 0 else 50000.0)), 2), 1.0)
        
        # Nivel de Riesgo
        if est_triangles > triangle_budget:
            risk = StrategyRiskLevel.CRITICAL
        elif complexity > 0.75:
            risk = StrategyRiskLevel.HIGH
        elif complexity > 0.40:
            risk = StrategyRiskLevel.MEDIUM
        else:
            risk = StrategyRiskLevel.LOW

        # Score de Estrategia
        score = round(max(0.0, 1.0 - (complexity * 0.15) - (0.25 if risk == StrategyRiskLevel.HIGH else 0.0)), 2)

        return CostEstimate(
            estimated_triangles=est_triangles,
            estimated_objects=num_objects,
            estimated_modifiers=num_modifiers,
            complexity_score=complexity,
            risk_level=risk,
            strategy_score=score
        )
