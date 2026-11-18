from typing import List, Dict, Any, Optional
from ..nodes.graph_node import GraphNode
from ..nodes.node_types import NodeType
from ..edges.edge_types import RelationshipType
from ..queries.graph_query_engine import GraphQueryEngine

class GraphProvenanceTracker:
    """
    Traces structural and operational provenance chains:
    REFERENCE -> REQUIREMENT -> DECISION -> OPERATION -> ASSET -> EVALUATION -> DELIVERY.
    """
    def __init__(self, query_engine: GraphQueryEngine):
        self.queries = query_engine

    def trace_lineage(self, asset_node_id: str) -> Dict[str, Any]:
        lineage = {
            "asset_id": asset_node_id,
            "references": [],
            "requirements": [],
            "decisions": [],
            "operations": [],
            "materials": [],
            "evaluations": [],
            "deliveries": []
        }

        # Find materials
        materials = self.queries.find_related(asset_node_id, RelationshipType.USES)
        lineage["materials"] = [m.node_id for m in materials]

        # Find evaluations
        evaluations = self.queries.find_related(asset_node_id, RelationshipType.EVALUATED_BY)
        lineage["evaluations"] = [e.node_id for e in evaluations]

        # Find incoming operations
        for node, edge in self.queries.neighbors(asset_node_id, direction="IN"):
            if edge.relationship_type == RelationshipType.MODIFIES and node.node_type == NodeType.OPERATION:
                lineage["operations"].append(node.node_id)
            elif edge.relationship_type == RelationshipType.DERIVED_FROM and node.node_type == NodeType.REFERENCE:
                lineage["references"].append(node.node_id)
            elif edge.relationship_type == RelationshipType.SATISFIES and node.node_type == NodeType.REQUIREMENT:
                lineage["requirements"].append(node.node_id)
            elif edge.relationship_type == RelationshipType.AFFECTS and node.node_type == NodeType.DECISION:
                lineage["decisions"].append(node.node_id)
            elif edge.relationship_type == RelationshipType.DELIVERED_AS and node.node_type == NodeType.DELIVERY:
                lineage["deliveries"].append(node.node_id)

        return lineage
