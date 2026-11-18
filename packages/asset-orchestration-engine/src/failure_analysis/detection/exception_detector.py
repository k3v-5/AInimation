import traceback
import time
from typing import Dict, Any, Optional
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureType, FailureSeverity, FailureStatus
from ..core.failure_classifier import FailureClassifier
from ..core.failure_context import FailureContext

class ExceptionDetector:
    """Detects and packages runtime Python exceptions into FailureRecords."""

    @staticmethod
    def capture(
        exc: Exception,
        semantic_id: str,
        context: Optional[FailureContext] = None,
        failure_id: Optional[str] = None
    ) -> FailureRecord:
        msg = str(exc)
        st = traceback.format_exc()
        if st.strip() == "NoneType: None":
            st = "".join(traceback.format_stack())

        f_type, cat, sev = FailureClassifier.classify(msg)
        f_id = failure_id or f"FAIL_{int(context.timestamp * 1000) if context else int(time.time()*1000)}_{semantic_id.replace('.', '_')}"

        return FailureRecord(
            failure_id=f_id,
            semantic_id=semantic_id,
            message=msg,
            exception_type=type(exc).__name__,
            exception_message=msg,
            stack_trace=st,
            failure_type=f_type,
            failure_category=cat,
            severity=sev,
            status=FailureStatus.DETECTED,
            job_id=context.job_id if context else None,
            agent_id=context.agent_id if context else "agent.visual.critic",
            contract_id=context.contract_id if context else "contract.critic.v2",
            capability=context.capability if context else "CAP_GEOMETRY",
            tool=context.tool if context else "BlenderTool",
            pipeline_phase=context.pipeline_phase if context else "PHASE_77",
            pipeline_stage=context.pipeline_stage if context else "EXECUTION",
            checkpoint_id=context.checkpoint_id if context else None,
            input_snapshot=context.input_params if context else {}
        )
