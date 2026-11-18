from typing import Optional
from ...knowledge_graph import (
    ProjectKnowledgeGraphAPI, GraphNode, NodeType, GraphEdge, RelationshipType
)
from ..models.evaluation_models import EvaluationBenchmark

class KnowledgeGraphEvaluationBridge:
    """Bridges EvaluationBenchmark records into the F74 Project Knowledge Graph."""
    def __init__(self, kg_api: Optional[ProjectKnowledgeGraphAPI] = None):
        self.kg = kg_api or ProjectKnowledgeGraphAPI()

    def sync_benchmark_to_graph(self, benchmark: EvaluationBenchmark):
        # 1. Create or update Evaluation node
        eval_node_id = f"EVAL_{benchmark.benchmark_id}"
        eval_node = GraphNode(
            node_id=eval_node_id,
            node_type=NodeType.EVALUATION,
            semantic_id=f"{benchmark.asset_semantic_id}.eval",
            metadata={
                "weighted_score": round(benchmark.weighted_score, 4),
                "acceptance": benchmark.acceptance.value,
                "confidence": round(benchmark.confidence, 4)
            }
        )
        self.kg.add_node(eval_node, agent_id=benchmark.agent_id or "agent.visual.critic")

        # 2. Connect to Asset node
        asset_node_id = f"ASSET_{benchmark.asset_semantic_id}"
        if self.kg.get_node(asset_node_id):
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_{asset_node_id}_EVAL_{eval_node_id}",
                source_node=asset_node_id,
                target_node=eval_node_id,
                relationship_type=RelationshipType.EVALUATED_BY,
                job_id=benchmark.job_id,
                agent_id=benchmark.agent_id
            ))

        # 3. Create Defect nodes
        for defect in benchmark.defects:
            def_node_id = f"DEFECT_{defect.defect_id}"
            def_node = GraphNode(
                node_id=def_node_id,
                node_type=NodeType.DEFECT,
                metadata={
                    "severity": defect.severity.value,
                    "dimension": defect.dimension.value,
                    "description": defect.description
                }
            )
            self.kg.add_node(def_node, agent_id=benchmark.agent_id or "agent.visual.critic")
            self.kg.add_edge(GraphEdge(
                edge_id=f"EDGE_{eval_node_id}_IDENTIFIES_{def_node_id}",
                source_node=eval_node_id,
                target_node=def_node_id,
                relationship_type=RelationshipType.IDENTIFIES,
                job_id=benchmark.job_id,
                agent_id=benchmark.agent_id
            ))
