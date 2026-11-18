from typing import List, Dict, Any
from ..core.critic_schema import (
    DiagnosticGraph, CriticDiagnosis, RootCause, CorrectionAction
)

class DiagnosticGraphBuilder:
    @classmethod
    def build_graph(
        cls,
        diagnoses: List[CriticDiagnosis],
        root_causes: List[RootCause],
        actions: List[CorrectionAction]
    ) -> DiagnosticGraph:
        nodes = []
        edges = []

        # Nodes
        for d in diagnoses:
            nodes.append({"id": d.diagnosis_id, "type": "DIAGNOSIS", "label": d.category.value})
        for c in root_causes:
            nodes.append({"id": c.cause_id, "type": "ROOT_CAUSE", "label": c.category.value})
        for a in actions:
            nodes.append({"id": a.action_id, "type": "CORRECTION_ACTION", "label": a.target})

        # Edges
        for d in diagnoses:
            for c in d.probable_causes:
                edges.append({"source": d.diagnosis_id, "target": c.cause_id, "relation": "CAUSED_BY"})
        for a in actions:
            edges.append({"source": "PLAN", "target": a.action_id, "relation": "EXECUTES"})

        return DiagnosticGraph(nodes=nodes, edges=edges)
