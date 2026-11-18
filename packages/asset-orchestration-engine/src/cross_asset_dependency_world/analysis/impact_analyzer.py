from typing import Dict, Any, List, Set, Optional
from ..core.world_types import (
    NodeType, EdgeType, DependencyStrength, DirtyState,
    ChangeCategory, ImpactLevel
)
from ..core.world_schema import WorldNode, WorldEdge, ImpactReport
from ..graph.world_dependency_graph import WorldDependencyGraph

class ImpactAnalyzer:
    @classmethod
    def analyze_change(
        cls,
        graph: WorldDependencyGraph,
        target_node_id: str,
        category: ChangeCategory,
        details: Optional[Dict[str, Any]] = None
    ) -> ImpactReport:
        if target_node_id not in graph.nodes:
            raise KeyError(f"Target node '{target_node_id}' does not exist in graph.")

        direct_impacts: List[str] = graph.get_consumers(target_node_id)
        indirect_impacts: List[str] = []
        visited = set(direct_impacts)
        visited.add(target_node_id)

        # Recorrer consumidores indirectos
        queue = list(direct_impacts)
        while queue:
            curr = queue.pop(0)
            for consumer in graph.get_consumers(curr):
                if consumer not in visited:
                    visited.add(consumer)
                    indirect_impacts.append(consumer)
                    queue.append(consumer)

        all_affected = set(direct_impacts).union(set(indirect_impacts))
        unaffected = [nid for nid in graph.nodes if nid != target_node_id and nid not in all_affected]

        # Diferenciación de categoría de cambio
        requires_geom = True
        requires_mat = False

        if category == ChangeCategory.MATERIAL:
            requires_geom = False
            requires_mat = True

        # Filtrar potenciales impactos según dependencias reales (LOD, Colisión, Navegación, Blueprints)
        potential_impacts = [
            nid for nid in direct_impacts
            if graph.nodes[nid].node_type in [NodeType.COLLISION, NodeType.LOD, NodeType.NAVIGATION, NodeType.BLUEPRINT]
        ]

        return ImpactReport(
            source_node_id=target_node_id,
            change_category=category,
            direct_impacts=direct_impacts,
            indirect_impacts=indirect_impacts,
            potential_impacts=potential_impacts,
            unaffected_nodes=unaffected,
            requires_geometry_regeneration=requires_geom,
            requires_material_update=requires_mat
        )

    @classmethod
    def evaluate_delete_safety(
        cls,
        graph: WorldDependencyGraph,
        node_id: str
    ) -> Dict[str, Any]:
        if node_id not in graph.nodes:
            raise KeyError(f"Node '{node_id}' does not exist.")

        consumers = graph.get_consumers(node_id)
        critical_deps = [
            cid for cid in consumers
            if graph.nodes[cid].node_type in [NodeType.BLUEPRINT, NodeType.GAMEPLAY_REFERENCE, NodeType.NAVIGATION]
        ]

        is_safe = len(critical_deps) == 0

        return {
            "node_id": node_id,
            "is_safe_to_delete": is_safe,
            "direct_consumers_count": len(consumers),
            "critical_dependencies": critical_deps,
            "warning": f"Node '{node_id}' has {len(critical_deps)} critical gameplay/blueprint references." if not is_safe else "Safe to delete."
        }
