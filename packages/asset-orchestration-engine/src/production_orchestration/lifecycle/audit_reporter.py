import json
from typing import Dict, Any, List
from ..core.production_job import ProductionJob
from ..core.stage_models import StageResult

class AuditReporter:
    """Generates complete auditable JSON manifests for ProductionJobs."""

    @staticmethod
    def generate_manifest(job: ProductionJob, plan: Dict[str, Any], stages: List[StageResult]) -> Dict[str, Any]:
        return {
            "manifest_version": "1.0.0",
            "job": job.to_dict(),
            "plan": plan,
            "stage_summary": [s.to_dict() for s in stages],
            "final_status": job.status.value
        }

    @staticmethod
    def generate_events(stages: List[StageResult]) -> List[Dict[str, Any]]:
        return [
            {
                "stage": s.stage_id.value,
                "status": s.status.value,
                "agent": s.agent_id,
                "started_at": s.started_at,
                "completed_at": s.completed_at,
                "errors": s.errors
            }
            for s in stages
        ]

    @staticmethod
    def generate_metrics(job: ProductionJob, stages: List[StageResult]) -> Dict[str, Any]:
        total_time = sum((s.completed_at - s.started_at) for s in stages if s.completed_at)
        return {
            "total_execution_time": round(total_time, 2),
            "stages_executed": len(stages),
            "quality_threshold": job.quality_threshold,
            "status": job.status.value
        }

    @staticmethod
    def generate_decision_log(job: ProductionJob) -> List[Dict[str, Any]]:
        return [
            {"decision": "STRATEGY_SELECTED", "strategy": job.strategy},
            {"decision": "FINAL_DECISION", "status": job.status.value}
        ]
