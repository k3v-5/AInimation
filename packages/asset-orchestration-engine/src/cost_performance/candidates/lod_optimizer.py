from typing import List, Dict, Any

class LODOptimizer:
    """Evaluates LOD distribution, triangle decimation ratios, and transition smoothness."""

    @staticmethod
    def evaluate_lods(lod_triangle_counts: List[int]) -> Dict[str, Any]:
        if not lod_triangle_counts or len(lod_triangle_counts) < 2:
            return {"status": "NEEDS_LOD_GENERATION", "recommended_levels": 3}

        base = lod_triangle_counts[0]
        ratios = [round(c / max(1, base), 2) for c in lod_triangle_counts]

        # Ideal ratios: [1.0, 0.5, 0.25]
        return {
            "lod_levels": len(lod_triangle_counts),
            "triangle_counts": lod_triangle_counts,
            "ratios": ratios,
            "status": "OPTIMAL_LOD_CHAIN" if len(lod_triangle_counts) >= 3 else "ACCEPTABLE"
        }

class CollisionOptimizer:
    """Evaluates physical convex hull count, bounding volumes, and collision adequacy."""

    @staticmethod
    def evaluate_collision(hull_count: int, max_budget: int = 12) -> Dict[str, Any]:
        if hull_count > max_budget:
            status = "OVER_BUDGET"
            recommendation = "Merge adjacent convex hulls"
        elif hull_count == 0:
            status = "MISSING_COLLISION"
            recommendation = "Generate UCX convex hull"
        else:
            status = "OPTIMAL"
            recommendation = "Collision within physics budget"

        return {
            "hull_count": hull_count,
            "max_budget": max_budget,
            "status": status,
            "recommendation": recommendation
        }
