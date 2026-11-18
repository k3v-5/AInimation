from typing import Optional, Dict, Any
from ...knowledge_graph import ProjectKnowledgeGraphAPI, GraphNode, GraphEdge, NodeType, RelationshipType

class KnowledgeGraphBridge:
    """Connects Failure Analysis events and root causes into the F74 Project Knowledge Graph."""

    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def record_failure_node(self, failure_id: str, semantic_id: str, failure_type: str, severity: str):
        node = GraphNode(
            node_id=f"failure:{failure_id}",
            node_type=NodeType.DEFECT,
            semantic_id=f"failure.{failure_id}",
            metadata={"failure_id": failure_id, "severity": severity, "type": failure_type}
        )
        self.kg.add_node(node)

    def record_root_cause_node(self, cause_id: str, failure_id: str, category: str, description: str):
        node = GraphNode(
            node_id=f"root_cause:{cause_id}",
            node_type=NodeType.DECISION,
            semantic_id=f"root_cause.{cause_id}",
            metadata={"cause_id": cause_id, "category": category, "description": description}
        )
        self.kg.add_node(node)
