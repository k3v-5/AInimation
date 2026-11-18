from typing import Dict, Any, List, Optional
from ..core.world_types import (
    NodeType, EdgeType, DependencyStrength, DirtyState,
    ImpactLevel, ChangeCategory
)
from ..core.world_schema import (
    WorldNode, WorldEdge, ImpactReport, RegenerationPlan,
    WorldSnapshotRecord, WorldChangeProposal
)
from ..graph.world_dependency_graph import WorldDependencyGraph
from ..analysis.impact_analyzer import ImpactAnalyzer
from ..planner.world_regeneration_planner import WorldRegenerationPlanner

class WorldDependencyAPI:
    """
    Cross-Asset Dependency & World Building API (AOE v47)
    
    Regla Fundamental:
    LA IA NUNCA ASUME QUE UN CAMBIO REQUIERE REHACER EL MUNDO COMPLETO.
    ANALIZA EL GRAFO DE DEPENDENCIAS, DETERMINA CONSUMIDORES DIRECTOS E INDIRECTOS,
    AISLA CONTEXTOS DE MUNDO, DISCRIMINA CAMBIOS MATERIALES VS GEOMÉTRICOS Y REGENERA EN ORDEN TOPOLÓGICO.
    """
    def __init__(self):
        self.graph = WorldDependencyGraph()
        self.snapshots: Dict[str, WorldSnapshotRecord] = {}

    def register_node(
        self,
        node_id: str,
        name: str,
        node_type: NodeType,
        world_id: str = "DEFAULT_WORLD",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorldNode:
        node = WorldNode(
            node_id=node_id,
            name=name,
            node_type=node_type,
            world_id=world_id,
            version=version,
            metadata=metadata or {}
        )
        self.graph.add_node(node)
        return node

    def register_dependency(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        edge_type: EdgeType = EdgeType.DEPENDS_ON,
        strength: DependencyStrength = DependencyStrength.HARD,
        allows_propagation: bool = True
    ) -> WorldEdge:
        edge = WorldEdge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            strength=strength,
            allows_propagation=allows_propagation
        )
        self.graph.add_edge(edge)
        return edge

    def analyze_change_impact(
        self,
        target_node_id: str,
        category: ChangeCategory = ChangeCategory.STRUCTURAL,
        details: Optional[Dict[str, Any]] = None
    ) -> ImpactReport:
        return ImpactAnalyzer.analyze_change(self.graph, target_node_id, category, details)

    def evaluate_delete_safety(self, node_id: str) -> Dict[str, Any]:
        return ImpactAnalyzer.evaluate_delete_safety(self.graph, node_id)

    def plan_regeneration(
        self,
        dirty_node_ids: List[str],
        world_context_id: Optional[str] = None
    ) -> RegenerationPlan:
        return WorldRegenerationPlanner.plan_regeneration(self.graph, dirty_node_ids, world_context_id)

    def detect_cycles(self) -> Optional[List[str]]:
        return self.graph.detect_cycles()

    def get_consumers(self, node_id: str) -> List[str]:
        return self.graph.get_consumers(node_id)

    def get_dependencies(self, node_id: str) -> List[str]:
        return self.graph.get_dependencies(node_id)

    def create_snapshot(self, world_id: str = "DEFAULT_WORLD") -> WorldSnapshotRecord:
        snap = WorldSnapshotRecord(
            snapshot_id=f"SNAP_{world_id}_{len(self.snapshots) + 1:03d}",
            world_id=world_id,
            node_count=len(self.graph.nodes),
            edge_count=len(self.graph.edges)
        )
        self.snapshots[snap.snapshot_id] = snap
        return snap
