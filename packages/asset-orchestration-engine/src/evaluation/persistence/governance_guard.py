from typing import Optional
from ...governance import AgentContractsToolGovernanceAPI, Permission
from ..models.evaluation_models import EvaluationBenchmark
from ..core.evaluation_types import BenchmarkStatus

class EvaluationPermissionDeniedError(Exception):
    """Raised when an agent attempts unauthorized benchmark modifications."""
    pass

class EvaluationGovernanceGuard:
    """Enforces F72 governance and permission rules on benchmark lifecycle operations."""
    def __init__(self, gov_api: Optional[AgentContractsToolGovernanceAPI] = None):
        self.gov = gov_api or AgentContractsToolGovernanceAPI()

    def validate_evaluation_access(self, agent_id: str):
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            raise EvaluationPermissionDeniedError(f"Agent {agent_id} has no registered contract for evaluation.")

    def validate_benchmark_mutation(self, agent_id: str, benchmark: EvaluationBenchmark):
        if benchmark.status == BenchmarkStatus.FINALIZED:
            raise EvaluationPermissionDeniedError(f"Agent {agent_id} cannot mutate FINALIZED benchmark {benchmark.benchmark_id}.")
