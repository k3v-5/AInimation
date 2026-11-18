from typing import Optional, Dict, Any
from ...knowledge_graph import ProjectKnowledgeGraphAPI, GraphNode, GraphEdge, NodeType, RelationshipType

class KnowledgeGraphBridge:
    """Connects strategy learning records into F74 Project Knowledge Graph."""

    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def record_strategy_node(self, strategy_id: str, asset_type: str, quality_score: float):
        node = GraphNode(
            node_id=f"strategy:{strategy_id}",
            node_type=NodeType.DECISION,
            semantic_id=f"strategy.{strategy_id}",
            metadata={"strategy_id": strategy_id, "asset_type": asset_type, "quality_score": quality_score}
        )
        self.kg.add_node(node)
