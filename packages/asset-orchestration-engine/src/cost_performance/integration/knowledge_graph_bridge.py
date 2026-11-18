from typing import Optional, Dict, Any
from ...knowledge_graph import ProjectKnowledgeGraphAPI, GraphNode, GraphEdge, NodeType, RelationshipType

class KnowledgeGraphBridge:
    """Records optimization runs, tradeoffs, and decisions in F74 Knowledge Graph."""

    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def record_optimization_node(self, plan_id: str, semantic_id: str, selected_strategy_id: str, quality_score: float):
        node = GraphNode(
            node_id=f"opt_plan:{plan_id}",
            node_type=NodeType.DECISION,
            semantic_id=f"optimization.{semantic_id}",
            metadata={
                "plan_id": plan_id,
                "selected_strategy_id": selected_strategy_id,
                "quality_score": quality_score
            }
        )
        self.kg.add_node(node)
