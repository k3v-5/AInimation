from typing import Dict, Any, List
from ..core.msp_schema import GeometryBudgetDistribution

class BudgetDistributor:
    @classmethod
    def distribute_budget(
        cls,
        total_triangles: int,
        components: List[Dict[str, Any]]
    ) -> GeometryBudgetDistribution:
        if not components:
            return GeometryBudgetDistribution(total_triangles, total_triangles // 2, {})

        total_weight = sum(float(c.get("visual_weight", 1.0)) * (1.5 if c.get("is_primary", False) else 1.0) for c in components)
        if total_weight <= 0:
            total_weight = 1.0

        budgets = {}
        for c in components:
            cid = c.get("component_id", f"comp_{len(budgets)+1}")
            weight = float(c.get("visual_weight", 1.0)) * (1.5 if c.get("is_primary", False) else 1.0)
            allocated = int((weight / total_weight) * total_triangles)
            budgets[cid] = max(allocated, 200) # Mínimo 200 tris por componente

        return GeometryBudgetDistribution(
            total_triangle_budget=total_triangles,
            total_vertex_budget=total_triangles // 2,
            component_budgets=budgets
        )
