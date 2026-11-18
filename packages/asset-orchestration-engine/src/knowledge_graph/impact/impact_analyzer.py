from dataclasses import dataclass, field
from typing import List, Dict, Set
from ..nodes.node_types import NodeType
from ..nodes.graph_node import GraphNode
from ..edges.edge_types import RelationshipType
from ..queries.graph_query_engine import GraphQueryEngine

@dataclass
class ImpactReport:
    target_node_id: str
    direct_dependencies: List[str] = field(default_factory=list)
    indirect_dependencies: List[str] = field(default_factory=list)
    affected_assets: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    affected_jobs: List[str] = field(default_factory=list)
    affected_deliveries: List[str] = field(default_factory=list)
    affected_evaluations: List[str] = field(default_factory=list)
    regeneration_candidates: List[str] = field(default_factory=list)

class GraphImpactAnalyzer:
    """
    Performs precise impact analysis and computes minimal regeneration sets
    when nodes or materials are modified.
    """
    def __init__(self, query_engine: GraphQueryEngine):
        self.queries = query_engine

    def analyze_impact(self, node_id: str) -> ImpactReport:
        dependents = self.queries.find_dependents(node_id)
        direct_deps = [n.node_id for n, _ in self.queries.neighbors(node_id, direction="IN")]
        indirect_deps = [n.node_id for n in dependents if n.node_id not in direct_deps]

        report = ImpactReport(
            target_node_id=node_id,
            direct_dependencies=direct_deps,
            indirect_dependencies=indirect_deps
        )

        all_affected = [self.queries.get_node(node_id)] + dependents
        for n in all_affected:
            if not n:
                continue
            if n.node_type == NodeType.ASSET:
                if n.node_id not in report.affected_assets:
                    report.affected_assets.append(n.node_id)
            elif n.node_type == NodeType.ASSET_COMPONENT:
                if n.node_id not in report.affected_components:
                    report.affected_components.append(n.node_id)
            elif n.node_type == NodeType.JOB:
                if n.node_id not in report.affected_jobs:
                    report.affected_jobs.append(n.node_id)
            elif n.node_type == NodeType.DELIVERY:
                if n.node_id not in report.affected_deliveries:
                    report.affected_deliveries.append(n.node_id)
            elif n.node_type == NodeType.EVALUATION:
                if n.node_id not in report.affected_evaluations:
                    report.affected_evaluations.append(n.node_id)

        # Minimal Regeneration Candidates: direct components + assets
        report.regeneration_candidates = list(set(report.affected_components + report.affected_assets))
        return report
