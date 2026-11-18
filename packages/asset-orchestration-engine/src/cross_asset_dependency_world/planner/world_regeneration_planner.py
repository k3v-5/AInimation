import time
from typing import Dict, Any, List, Set, Optional
from ..core.world_types import DirtyState
from ..core.world_schema import RegenerationPlan
from ..graph.world_dependency_graph import WorldDependencyGraph

class WorldRegenerationPlanner:
    @classmethod
    def plan_regeneration(
        cls,
        graph: WorldDependencyGraph,
        dirty_node_ids: List[str],
        world_context_id: Optional[str] = None
    ) -> RegenerationPlan:
        # 1. Comprobar ciclos
        cycles = graph.detect_cycles()
        if cycles:
            raise ValueError(f"DEPENDENCY_CYCLE_DETECTED: Graph contains circular dependency cycle {cycles}. Cannot plan regeneration.")

        # 2. Filtrar por contexto de mundo (Aislamiento de Mundos)
        target_nodes = []
        for nid in dirty_node_ids:
            if nid in graph.nodes:
                if world_context_id is None or graph.nodes[nid].world_id == world_context_id:
                    target_nodes.append(nid)

        # 3. Ordenamiento Topológico (Kahn's Algorithm o DFS post-order)
        # Nodos que deben construirse primero: los que no tienen dependencias pendientes entre los dirty
        in_degree = {nid: 0 for nid in target_nodes}
        target_set = set(target_nodes)

        for nid in target_nodes:
            for dep in graph.get_dependencies(nid):
                if dep in target_set:
                    in_degree[nid] += 1

        queue = [nid for nid in target_nodes if in_degree[nid] == 0]
        execution_order = []
        batches = []

        while queue:
            current_batch = list(queue)
            batches.append(current_batch)
            queue = []

            for u in current_batch:
                execution_order.append(u)
                for consumer in graph.get_consumers(u):
                    if consumer in in_degree:
                        in_degree[consumer] -= 1
                        if in_degree[consumer] == 0:
                            queue.append(consumer)

        plan_id = f"RPLAN_{int(time.time()*1000)}"

        return RegenerationPlan(
            plan_id=plan_id,
            execution_order=execution_order,
            dirty_nodes=target_nodes,
            parallel_batches=batches,
            estimated_mcp_calls=len(execution_order)
        )
