import time
import traceback
import sys
from typing import Dict, Any, Optional
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureStatus, FailureType
from ..core.severity import FailureSeverity
from .exception_normalizer import ExceptionNormalizer

class FailureCapture:
    """Captures runtime failures, exceptions, and evaluation rejects into standardized FailureRecords."""
    
    @classmethod
    def capture_exception(
        cls,
        exc: Exception,
        semantic_id: str,
        operation: str = "GENERATE_ASSET",
        agent_id: str = "agent.visual.critic",
        failure_id: Optional[str] = None,
        job_id: Optional[str] = None,
        tool: str = "BlenderTool",
        capability: str = "CAP_GEOMETRY",
        resource: str = "weapon_vandal",
        state_before: Optional[Dict[str, Any]] = None
    ) -> FailureRecord:
        raw_msg = str(exc)
        exc_type = type(exc).__name__
        st = traceback.format_exc()
        if st.strip() == "NoneType: None":
            st = "".join(traceback.format_stack())

        f_type, err_code, norm_msg, sev = ExceptionNormalizer.normalize(raw_msg)
        f_id = failure_id or f"FAIL_{int(time.time() * 1000)}_{semantic_id.replace('.', '_')}"

        return FailureRecord(
            failure_id=f_id,
            semantic_id=semantic_id,
            message=raw_msg,
            job_id=job_id,
            operation=operation,
            agent_id=agent_id,
            failure_type=f_type,
            severity=sev,
            error_code=err_code,
            normalized_message=norm_msg,
            exception_type=exc_type,
            stack_trace=st,
            tool=tool,
            capability=capability,
            resource=resource,
            state_before=state_before or {},
            status=FailureStatus.DETECTED
        )
