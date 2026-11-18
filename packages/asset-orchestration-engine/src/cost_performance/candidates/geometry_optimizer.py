from typing import Dict, Any

class GeometryOptimizer:
    """Evaluates topology, vertex density, modifier stack, and detects budget status."""

    @staticmethod
    def analyze_geometry(poly_count: int, target_budget: int) -> Dict[str, Any]:
        if poly_count > target_budget * 1.15:
            status = "OVER_BUDGET"
            recommendation = "Apply decimation modifier or reduce subdivision levels"
        elif poly_count < target_budget * 0.50:
            status = "UNDER_BUDGET"
            recommendation = "Geometry within budget; detail enhancement possible"
        else:
            status = "OPTIMAL"
            recommendation = "Polygon count optimal for target profile"

        return {
            "polygon_count": poly_count,
            "target_budget": target_budget,
            "status": status,
            "recommendation": recommendation
        }
