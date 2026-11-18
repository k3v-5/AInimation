from typing import Dict, Any, List, Tuple
from ..core.scene_schema import SceneBuildPlan, SceneBudget

class SceneOptimizer:
    @staticmethod
    def optimize_scene(plan: SceneBuildPlan, budget: SceneBudget, simulated_triangles: int) -> Tuple[bool, int, List[str]]:
        actions = []
        current_triangles = simulated_triangles

        if current_triangles > budget.max_triangles:
            actions.append(f"BUDGET_EXCEEDED: Scene triangles ({current_triangles}) exceeds max allowed ({budget.max_triangles}).")

            # Estrategia 1: Instanciación de casas repetidas
            houses = [inst for inst in plan.instances.values() if inst.asset_type == "HOUSE"]
            if len(houses) > 1:
                canonical = houses[0]
                for h in houses[1:]:
                    h.is_instance_of_id = canonical.instance_id
                actions.append(f"OPTIMIZATION: Instanced {len(houses)-1} secondary houses referencing '{canonical.instance_id}'.")
                # Reducción simulada de coste de memoria/triángulos
                current_triangles = int(current_triangles * 0.40)

        is_compliant = current_triangles <= budget.max_triangles
        return is_compliant, current_triangles, actions
