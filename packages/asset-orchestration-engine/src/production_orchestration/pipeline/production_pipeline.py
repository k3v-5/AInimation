import time
from typing import Dict, Any, List, Optional
from ..core.production_job import ProductionJob, JobStatus
from ..core.stage_models import PipelineStage, StageResult, StageStatus
from ..core.state_machine import ProductionStateMachine
from .stage_executor import StageExecutor
from .budget_enforcer import BudgetEnforcer

class ProductionPipeline:
    """Coordinates end-to-end 19-stage asset production execution."""

    def __init__(self, job: ProductionJob):
        self.job = job
        self.stage_results: List[StageResult] = []

    def execute_stage(
        self,
        stage: PipelineStage,
        agent_id: str,
        capabilities: List[str],
        stage_func,
        stage_args: Optional[Dict[str, Any]] = None
    ) -> StageResult:
        self.job.current_stage = stage.value
        self.job.current_agent = agent_id
        self.job.updated_at = time.time()

        res = StageExecutor.execute_stage(stage, agent_id, capabilities, stage_func, stage_args)
        self.stage_results.append(res)

        if res.status == StageStatus.FAILED:
            ProductionStateMachine.transition(self.job, JobStatus.FAILED)
            self.job.failure_state = {"stage": stage.value, "errors": res.errors}

        return res
