from typing import Optional
from ...knowledge_graph import (
    ProjectKnowledgeGraphAPI, GraphNode, NodeType, GraphEdge, RelationshipType
)
from ..core.failure_models import FailureRecord
from ..core.diagnostic_models import DiagnosticReport
from ..correction.corrective_action import CorrectiveAction

class DiagnosticsKnowledgeGraphBridge:
    """Bridges Diagnostics incidents, root causes, and corrective actions into the F74 Knowledge Graph."""
    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def record_incident_in_graph(
        self,
        failure: FailureRecord,
        report: DiagnosticReport,
        action: Optional[CorrectiveAction] = None,
        agent_id: str = "agent.visual.critic"
    ):
        # 1. Failure Node
        f_node_id = f"FAILURE_{failure.failure_id}"
        f_node = GraphNode(
            node_id=f_node_id,
            node_type=NodeType.OPERATION,
            semantic_id=f"failure.{failure.semantic_id}.{failure.failure_id}",
            metadata={
                "failure_type": failure.failure_type.value,
                "severity": failure.severity.value,
                "status": failure.status.value
            }
        )
        self.kg.add_node(f_node, agent_id=agent_id)

        # 2. Connect to Asset Node if exists
        asset_node_id = f"ASSET_{failure.semantic_id}"
        if self.kg.get_node(asset_node_id):
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_ASSET_AFFECTED_BY_{failure.failure_id}",
                source_node=asset_node_id,
                target_node=f_node_id,
                relationship_type=RelationshipType.HAS_OPERATION,
                agent_id=agent_id
            ))

        # 3. Action Node if exists
        if action:
            act_node_id = f"ACTION_{action.action_id}"
            act_node = GraphNode(
                node_id=act_node_id,
                node_type=NodeType.OPERATION,
                semantic_id=f"action.{failure.semantic_id}.{action.action_id}",
                metadata={
                    "action_type": action.action_type,
                    "target": action.target
                }
            )
            self.kg.add_node(act_node, agent_id=agent_id)
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_{f_node_id}_CORRECTED_BY_{act_node_id}",
                source_node=f_node_id,
                target_node=act_node_id,
                relationship_type=RelationshipType.SUPERSEDES,
                agent_id=agent_id
            ))
