from typing import Dict, Any, Optional
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureType, FailureSeverity, FailureStatus

class PipelineFailureDetector:
    """Detects orchestration and pipeline lifecycle failures."""

    @staticmethod
    def detect_step_failure(
        step_name: str,
        semantic_id: str,
        error_msg: str,
        job_id: Optional[str] = None
    ) -> FailureRecord:
        return FailureRecord(
            failure_id=f"FAIL_PIPE_{step_name}_{semantic_id.replace('.', '_')}",
            semantic_id=semantic_id,
            job_id=job_id,
            pipeline_phase="ORCHESTRATION",
            pipeline_stage=step_name,
            operation=step_name,
            failure_type=FailureType.UNKNOWN_ERROR,
            failure_category="PIPELINE",
            severity=FailureSeverity.ERROR,
            status=FailureStatus.DETECTED,
            message=f"Pipeline step '{step_name}' failed: {error_msg}"
        )
