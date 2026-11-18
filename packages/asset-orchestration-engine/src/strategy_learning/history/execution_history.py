from typing import Dict, Any, List, Optional

class ExecutionHistory:
    """Tracks execution traces linking job IDs, agent IDs, and strategy IDs."""

    def __init__(self):
        self._traces: List[Dict[str, Any]] = []

    def record_trace(self, job_id: str, agent_id: str, strategy_id: str, semantic_id: str, metadata: Optional[Dict[str, Any]] = None):
        self._traces.append({
            "job_id": job_id,
            "agent_id": agent_id,
            "strategy_id": strategy_id,
            "semantic_id": semantic_id,
            "metadata": metadata or {}
        })

    def list_traces(self) -> List[Dict[str, Any]]:
        return list(self._traces)
