from typing import Dict, Any, List, Optional
from ..nodes.node_types import NodeType
from ..nodes.graph_node import GraphNode
from ..edges.edge_types import RelationshipType
from ..edges.graph_edge import GraphEdge
from ..storage.graph_store import ProjectKnowledgeGraphStore, DuplicateSemanticIdentityError
from ..queries.graph_query_engine import GraphQueryEngine
from ..impact.impact_analyzer import GraphImpactAnalyzer, ImpactReport
from ..consistency.consistency_validator import GraphConsistencyValidator, GraphConsistencyReport, DependencyCycleDetectedError
from ..snapshots.graph_snapshot_service import GraphSnapshotService, GraphSnapshotRecord
from ..snapshots.graph_diff_engine import GraphDiff, GraphDiffEngine
from ..provenance.provenance_tracker import GraphProvenanceTracker
from ..integration.blender_extractor import BlenderGraphExtractor
from ..integration.governance_guard import GraphGovernanceGuard, GraphPermissionDeniedError

class ProjectKnowledgeGraphAPI:
    """
    Unified public facade for the Project Knowledge Graph (Phase 74).
    """
    def __init__(self, persistence_path: Optional[str] = None):
        self.store = ProjectKnowledgeGraphStore(persistence_path)
        self.queries = GraphQueryEngine(self.store)
        self.impact = GraphImpactAnalyzer(self.queries)
        self.consistency = GraphConsistencyValidator(self.store)
        self.snapshots = GraphSnapshotService(self.store)
        self.provenance = GraphProvenanceTracker(self.queries)
        self.blender = BlenderGraphExtractor(self.store)
        self.governance = GraphGovernanceGuard()
        self._init_project_root_nodes()

    def _init_project_root_nodes(self):
        if not self.store.get_node("PROJECT_DARX"):
            self.store.add_node(GraphNode(
                node_id="PROJECT_DARX",
                node_type=NodeType.PROJECT,
                semantic_id="darx.game.project",
                project_id="DarX",
                metadata={"title": "DarX Tactical Sci-Fi Project", "engine": "UE 5.4"}
            ))

    def add_node(self, node: GraphNode, agent_id: str = "agent.strategy") -> GraphNode:
        self.governance.validate_node_creation(agent_id, node.node_type)
        return self.store.add_node(node)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.store.get_node(node_id)

    def get_node_by_semantic_id(self, semantic_id: str) -> Optional[GraphNode]:
        return self.store.get_node_by_semantic_id(semantic_id)

    def add_edge(self, edge: GraphEdge, agent_id: str = "agent.strategy") -> GraphEdge:
        return self.store.add_edge(edge)

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        return self.store.get_edge(edge_id)

    def query_nodes(self, node_type: NodeType) -> List[GraphNode]:
        return self.queries.find_nodes(node_type)

    def get_dependencies(self, node_id: str) -> List[GraphNode]:
        return self.queries.find_dependencies(node_id)

    def get_dependents(self, node_id: str) -> List[GraphNode]:
        return self.queries.find_dependents(node_id)

    def analyze_impact(self, node_id: str) -> ImpactReport:
        return self.impact.analyze_impact(node_id)

    def validate_consistency(self) -> GraphConsistencyReport:
        return self.consistency.validate_consistency()

    def create_snapshot(self, snapshot_id: str) -> GraphSnapshotRecord:
        return self.snapshots.create_graph_snapshot(snapshot_id)

    def restore_snapshot(self, snapshot_id: str):
        self.snapshots.restore_graph_snapshot(snapshot_id)

    def compare_snapshots(self, snap_a: str, snap_b: str) -> GraphDiff:
        return self.snapshots.compare_graph_snapshots(snap_a, snap_b)

    def trace_lineage(self, asset_node_id: str) -> Dict[str, Any]:
        return self.provenance.trace_lineage(asset_node_id)

    def ingest_blender_scene(
        self,
        blend_file_path: str,
        scene_data: Dict[str, Any],
        semantic_asset_id: str,
        job_id: str = "JOB_INGEST",
        agent_id: str = "agent.blender.execution"
    ) -> List[str]:
        return self.blender.ingest_blender_scene_data(
            blend_file_path, scene_data, semantic_asset_id, job_id, agent_id
        )
