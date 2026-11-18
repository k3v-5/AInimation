import time
import hashlib
from typing import Dict, Any, List, Optional
from ..core.stage_models import PipelineStage, StageResult, StageStatus

class StageExecutor:
    """Executes atomic pipeline stages with hash tracking, timing, and error handling."""

    @staticmethod
    def execute_stage(
        stage: PipelineStage,
        agent_id: str,
        capabilities: List[str],
        stage_func,
        stage_args: Optional[Dict[str, Any]] = None
    ) -> StageResult:
        start_time = time.time()
        input_data = str(stage_args or {})
        input_hash = hashlib.sha256(input_data.encode("utf-8")).hexdigest()

        result = StageResult(
            stage_id=stage,
            status=StageStatus.RUNNING,
            input_hash=input_hash,
            started_at=start_time,
            agent_id=agent_id,
            capabilities_used=capabilities
        )

        try:
            output = stage_func(**(stage_args or {})) if stage_func else {}
            out_data = str(output or {})
            result.output_hash = hashlib.sha256(out_data.encode("utf-8")).hexdigest()
            result.status = StageStatus.COMPLETED
            result.completed_at = time.time()
            if isinstance(output, dict):
                result.metrics = output.get("metrics", {})
                result.artifacts_created = output.get("artifacts_created", [])
                result.artifacts_modified = output.get("artifacts_modified", [])
        except Exception as e:
            result.status = StageStatus.FAILED
            result.completed_at = time.time()
            result.errors.append(str(e))

        return result
