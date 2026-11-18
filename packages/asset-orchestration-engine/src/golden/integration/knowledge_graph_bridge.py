from typing import Optional
from ...knowledge_graph import (
    ProjectKnowledgeGraphAPI, GraphNode, NodeType, GraphEdge, RelationshipType
)
from ..core.golden_models import GoldenAsset

class KnowledgeGraphBridge:
    """Bridges Golden Assets into the F74 Project Knowledge Graph."""
    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def sync_golden(self, asset: GoldenAsset, agent_id: str = "agent.strategy"):
        g_node_id = f"GOLDEN_{asset.golden_id}"
        g_node = GraphNode(
            node_id=g_node_id,
            node_type=NodeType.ASSET,
            semantic_id=f"{asset.semantic_id}.golden.v{asset.version}",
            metadata={
                "golden_id": asset.golden_id,
                "version": asset.version,
                "status": asset.status.value,
                "baseline_score": round(asset.baseline_score, 4)
            }
        )
        self.kg.add_node(g_node, agent_id=agent_id)

        # Connect to base Asset node if present
        asset_node_id = f"ASSET_{asset.semantic_id}"
        if self.kg.get_node(asset_node_id):
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_{asset_node_id}_GOLDEN_{g_node_id}",
                source_node=asset_node_id,
                target_node=g_node_id,
                relationship_type=RelationshipType.HAS_VERSION,
                agent_id=agent_id
            ))

        # If has parent Golden ID
        if asset.parent_golden_id:
            parent_node_id = f"GOLDEN_{asset.parent_golden_id}"
            if self.kg.get_node(parent_node_id):
                self.kg.add_edge(GraphEdge(
                    edge_id=f"EDGE_{g_node_id}_SUPERSEDES_{parent_node_id}",
                    source_node=g_node_id,
                    target_node=parent_node_id,
                    relationship_type=RelationshipType.PREVIOUS_VERSION,
                    agent_id=agent_id
                ))
