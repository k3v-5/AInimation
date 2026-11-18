from typing import Optional
from ...knowledge_graph import (
    ProjectKnowledgeGraphAPI, GraphNode, NodeType, GraphEdge, RelationshipType
)
from ..models.golden_asset import GoldenAsset
from ..models.golden_baseline import GoldenBaseline

class GoldenKnowledgeGraphBridge:
    """Bridges Golden Assets, versions, and baselines into the F74 Project Knowledge Graph."""
    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def sync_golden_asset_to_graph(self, asset: GoldenAsset, agent_id: str = "agent.strategy"):
        g_node_id = f"GOLDEN_{asset.golden_asset_id}"
        g_node = GraphNode(
            node_id=g_node_id,
            node_type=NodeType.ASSET,
            semantic_id=asset.semantic_id,
            metadata={
                "golden_asset_id": asset.golden_asset_id,
                "current_version": asset.current_version,
                "status": asset.status.value,
                "asset_family": asset.asset_family,
                "category": asset.category
            }
        )
        self.kg.add_node(g_node, agent_id=agent_id)

        # Connect to base Asset node if exists
        asset_node_id = f"ASSET_{asset.semantic_id}"
        if self.kg.get_node(asset_node_id):
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_{asset_node_id}_PROMOTED_FROM_{g_node_id}",
                source_node=g_node_id,
                target_node=asset_node_id,
                relationship_type=RelationshipType.DERIVED_FROM,
                agent_id=agent_id
            ))

        # Create Version nodes
        for v_str, v_info in asset.versions.items():
            v_node_id = f"VER_{asset.golden_asset_id}_{v_str}".replace(".", "_")
            v_node = GraphNode(
                node_id=v_node_id,
                node_type=NodeType.VERSION,
                metadata={
                    "version": v_str,
                    "parent_version": v_info.parent_version,
                    "status": v_info.status.value
                }
            )
            self.kg.add_node(v_node, agent_id=agent_id)
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_{g_node_id}_HAS_VERSION_{v_node_id}",
                source_node=g_node_id,
                target_node=v_node_id,
                relationship_type=RelationshipType.HAS_VERSION,
                agent_id=agent_id
            ))
            if v_info.parent_version:
                parent_v_node_id = f"VER_{asset.golden_asset_id}_{v_info.parent_version}".replace(".", "_")
                if self.kg.get_node(parent_v_node_id):
                    self.kg.add_edge(GraphEdge(
                        edge_id=f"EDGE_{v_node_id}_SUPERSEDES_{parent_v_node_id}",
                        source_node=v_node_id,
                        target_node=parent_v_node_id,
                        relationship_type=RelationshipType.PREVIOUS_VERSION,
                        agent_id=agent_id
                    ))

    def sync_baseline_to_graph(self, baseline: GoldenBaseline, agent_id: str = "agent.strategy"):
        b_node_id = f"BASELINE_{baseline.baseline_id}"
        b_node = GraphNode(
            node_id=b_node_id,
            node_type=NodeType.EVALUATION,
            metadata={
                "golden_asset_id": baseline.golden_asset_id,
                "version": baseline.version,
                "global_score": baseline.global_score
            }
        )
        self.kg.add_node(b_node, agent_id=agent_id)
        g_node_id = f"GOLDEN_{baseline.golden_asset_id}"
        if self.kg.get_node(g_node_id):
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_{g_node_id}_EVALUATED_BY_{b_node_id}",
                source_node=g_node_id,
                target_node=b_node_id,
                relationship_type=RelationshipType.EVALUATED_BY,
                agent_id=agent_id
            ))
