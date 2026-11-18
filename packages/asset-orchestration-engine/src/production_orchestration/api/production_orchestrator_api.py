import time
from typing import Dict, Any, List, Optional, Tuple

from ..core.production_job import ProductionJob, JobStatus
from ..core.stage_models import PipelineStage, StageResult, StageStatus
from ..core.production_plan import ProductionPlan
from ..core.state_machine import ProductionStateMachine
from ..pipeline.production_pipeline import ProductionPipeline
from ..pipeline.stage_executor import StageExecutor
from ..pipeline.budget_enforcer import BudgetEnforcer
from ..lifecycle.version_manager import VersionManager
from ..lifecycle.crash_recovery_manager import CrashRecoveryManager
from ..lifecycle.cancellation_manager import CancellationManager
from ..lifecycle.audit_reporter import AuditReporter
from ..persistence.production_store import ProductionStore

from ..integration.multi_agent_bridge import MultiAgentBridge
from ..integration.recovery_bridge import RecoveryBridge
from ..integration.benchmark_bridge import BenchmarkBridge
from ..integration.golden_asset_bridge import GoldenAssetBridge
from ..integration.failure_analysis_bridge import FailureAnalysisBridge
from ..integration.strategy_learning_bridge import StrategyLearningBridge
from ..integration.cost_performance_bridge import CostPerformanceBridge
from ..integration.knowledge_graph_bridge import KnowledgeGraphBridge
from ..integration.packaging_delivery_bridge import PackagingDeliveryBridge

from ...evaluation import EvaluationBenchmarkAPI
from ...golden import GoldenAPI
from ...failure_analysis import FailureAnalysisAPI
from ...strategy_learning import StrategyLearningAPI
from ...cost_performance import CostPerformanceAPI

class ProductionOrchestratorAPI:
    """
    Unified public API for Phase 80: Production Orchestration.
    """
    def __init__(
        self,
        persistence_path: Optional[str] = None,
        eval_api: Optional[EvaluationBenchmarkAPI] = None,
        golden_api: Optional[GoldenAPI] = None,
        failure_api: Optional[FailureAnalysisAPI] = None,
        strat_api: Optional[StrategyLearningAPI] = None,
        cp_api: Optional[CostPerformanceAPI] = None
    ):
        self.store = ProductionStore(persistence_path)
        self.eval_bridge = BenchmarkBridge(eval_api)
        self.golden_bridge = GoldenAssetBridge(golden_api)
        self.failure_bridge = FailureAnalysisBridge(failure_api)
        self.strat_bridge = StrategyLearningBridge(strat_api)
        self.cp_bridge = CostPerformanceBridge(cp_api)
        self.multi_agent_bridge = MultiAgentBridge()
        self.recovery_bridge = RecoveryBridge()
        self.kg_bridge = KnowledgeGraphBridge()
        self.packaging_bridge = PackagingDeliveryBridge()

    def create_production_job(
        self,
        job_id: str,
        asset_semantic_id: str,
        asset_type: str = "WEAPON",
        input_specification: Optional[Dict[str, Any]] = None,
        reference_set: Optional[List[str]] = None,
        budget: Optional[Dict[str, Any]] = None,
        quality_threshold: float = 0.90
    ) -> ProductionJob:
        job = ProductionJob(
            job_id=job_id,
            asset_semantic_id=asset_semantic_id,
            asset_type=asset_type,
            input_specification=input_specification or {},
            reference_set=reference_set or [],
            budget=budget or {"max_execution_time": 180.0, "max_correction_iterations": 3, "max_memory_mb": 512.0},
            quality_threshold=quality_threshold,
            status=JobStatus.CREATED
        )
        self.store.store_job(job)
        self.kg_bridge.record_production_job(job.job_id, asset_semantic_id, job.status.value)
        return job

    def plan_production(
        self,
        job_id: str,
        items_to_create: Optional[List[str]] = None,
        items_to_modify: Optional[List[str]] = None
    ) -> ProductionPlan:
        job = self.store.get_job(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found.")

        plan_id = f"PLAN_{job.job_id}"
        plan = ProductionPlan(
            plan_id=plan_id,
            job_id=job.job_id,
            asset_semantic_id=job.asset_semantic_id,
            items_to_create=items_to_create or [f"SM_{job.asset_semantic_id}"],
            items_to_modify=items_to_modify or []
        )
        ok, msg = ProductionStateMachine.transition(job, JobStatus.PLANNED)
        if not ok:
            raise ValueError(f"Cannot plan job '{job_id}' in status {job.status.value}: {msg}")

        job.pipeline_plan = plan.to_dict()
        self.store.store_plan(plan_id, plan.to_dict())
        self.store.store_job(job)
        return plan

    def start_production(self, job_id: str) -> Tuple[bool, str]:
        job = self.store.get_job(job_id)
        if not job:
            return False, f"Job '{job_id}' not found."

        ok, msg = ProductionStateMachine.transition(job, JobStatus.RUNNING)
        if not ok:
            return False, msg
        self.store.store_job(job)
        return True, "Production started"

    def pause_production(self, job_id: str) -> Tuple[bool, str]:
        job = self.store.get_job(job_id)
        if not job:
            return False, f"Job '{job_id}' not found."

        ok, msg = ProductionStateMachine.transition(job, JobStatus.PAUSED)
        if not ok:
            return False, msg
        self.store.store_job(job)
        return True, "Production paused"

    def resume_production(self, job_id: str) -> Tuple[bool, str]:
        job = self.store.get_job(job_id)
        if not job:
            return False, f"Job '{job_id}' not found."

        ok, msg = ProductionStateMachine.transition(job, JobStatus.RUNNING)
        if not ok:
            return False, msg
        self.store.store_job(job)
        return True, "Production resumed"

    def cancel_production(self, job_id: str, reason: str = "User requested cancellation") -> Tuple[bool, str]:
        job = self.store.get_job(job_id)
        if not job:
            return False, f"Job '{job_id}' not found."

        success, msg = CancellationManager.cancel_job(job, reason)
        if success:
            self.store.store_job(job)
        return success, msg

    def get_production_status(self, job_id: str) -> Optional[JobStatus]:
        job = self.store.get_job(job_id)
        return job.status if job else None

    def get_production_plan(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.store.get_job(job_id)
        if not job:
            return None
        return job.pipeline_plan

    def get_production_events(self, job_id: str) -> List[Dict[str, Any]]:
        manifest = self.store.get_manifest(job_id)
        if not manifest:
            return []
        return manifest.get("stage_summary", [])

    def get_production_metrics(self, job_id: str) -> Dict[str, Any]:
        job = self.store.get_job(job_id)
        if not job:
            return {}
        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "attempt": job.attempt,
            "current_stage": job.current_stage
        }

    def get_production_artifacts(self, job_id: str) -> List[str]:
        manifest = self.store.get_manifest(job_id)
        if not manifest:
            return []
        artifacts = []
        for s in manifest.get("stage_summary", []):
            artifacts.extend(s.get("artifacts_created", []))
        return list(set(artifacts))

    def retry_production(self, job_id: str) -> Tuple[bool, str]:
        job = self.store.get_job(job_id)
        if not job:
            return False, f"Job '{job_id}' not found."

        if job.status not in (JobStatus.FAILED, JobStatus.REJECTED):
            return False, f"Cannot retry job in status {job.status.value}"

        ok1, msg1 = ProductionStateMachine.transition(job, JobStatus.RECOVERING)
        if not ok1:
            return False, msg1
        job.attempt += 1
        ok2, msg2 = ProductionStateMachine.transition(job, JobStatus.RUNNING)
        if not ok2:
            return False, msg2
        self.store.store_job(job)
        return True, "Job retry initiated"

    def approve_production(self, job_id: str) -> Tuple[bool, str]:
        job = self.store.get_job(job_id)
        if not job:
            return False, f"Job '{job_id}' not found."

        ok, msg = ProductionStateMachine.transition(job, JobStatus.COMPLETED)
        if not ok:
            return False, msg
        self.store.store_job(job)
        return True, "Production approved and marked COMPLETED"

    def reject_production(self, job_id: str, reason: str = "Quality or regression failure") -> Tuple[bool, str]:
        job = self.store.get_job(job_id)
        if not job:
            return False, f"Job '{job_id}' not found."

        ok, msg = ProductionStateMachine.transition(job, JobStatus.REJECTED)
        if not ok:
            return False, msg
        job.failure_state = {"rejection_reason": reason}
        self.store.store_job(job)
        return True, f"Production rejected: {reason}"

    def create_pipeline(self, job_id: str) -> ProductionPipeline:
        job = self.store.get_job(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found.")
        return ProductionPipeline(job)
