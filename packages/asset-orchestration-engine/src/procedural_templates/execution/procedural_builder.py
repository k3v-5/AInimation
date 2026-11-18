from typing import Dict, Any, Optional, Tuple
from ..core.construction_plan import ConstructionPlan
from .dependency_graph import ConstructionDependencyGraph
from ...correction_execution.providers.blender_provider import IBlenderProvider

class ProceduralBuilder:
    def __init__(self, provider: IBlenderProvider, max_operations_budget: int = 50):
        self.provider = provider
        self.max_operations_budget = max_operations_budget

    def build_asset(self, asset_id: str, plan: ConstructionPlan, dry_run: bool = False) -> Tuple[bool, str]:
        # 1. Comprobar presupuesto
        if len(plan.operations) > self.max_operations_budget:
            return False, f"CONSTRUCTION_BUDGET_EXCEEDED: Plan has {len(plan.operations)} operations (Max: {self.max_operations_budget})."

        # 2. Ordenación topológica
        ok_sort, sorted_ops, msg_sort = ConstructionDependencyGraph.sort_operations(plan.operations)
        if not ok_sort:
            return False, msg_sort

        if dry_run:
            return True, f"Dry run successful. {len(sorted_ops)} operations planned."

        # 3. Inicializar / resetear asset en el provider
        components_dict = {}
        for op in sorted_ops:
            if op.type == "CREATE_COMPONENT":
                components_dict[op.target_component] = {
                    "dimensions": op.parameters.get("dimensions", (0.1, 0.1, 0.1)),
                    "material": op.parameters.get("material", {})
                }
        self.provider.init_asset(asset_id, components_dict)

        return True, f"Asset '{asset_id}' constructed deterministically via template '{plan.template_id}'."
