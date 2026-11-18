from typing import Tuple, Optional, Dict

class BudgetValidator:
    @staticmethod
    def validate_polygon_budget(
        lod_triangles: Dict[str, int],
        budget_limits: Dict[str, int]
    ) -> Tuple[bool, Optional[str]]:
        for lod_name, tri_count in lod_triangles.items():
            limit = budget_limits.get(lod_name)
            if limit is not None and tri_count > limit:
                return False, f"POLYGON_BUDGET_EXCEEDED: {lod_name} has {tri_count} triangles, exceeding budget limit of {limit}."
        return True, None
