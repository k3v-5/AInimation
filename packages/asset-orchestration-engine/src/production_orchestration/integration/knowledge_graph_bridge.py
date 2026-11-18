from typing import Optional, Dict, Any
from ...knowledge_graph import ProjectKnowledgeGraphAPI, GraphNode, GraphEdge, NodeType, RelationshipType

class KnowledgeGraphBridge:
    """Connects production jobs and artifacts to F74 Project Knowledge Graph."""

    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def record_production_job(self, job_id: str, semantic_id: str, status: str):
        node = GraphNode(
            node_id=f"prod_job:{job_id}",
            node_type=NodeType.OPERATION,
            semantic_id=f"job.{semantic_id}",
            metadata={"job_id": job_id, "status": status}
        )
        self.kg.add_node(node)
