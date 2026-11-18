from typing import Dict, Any, List, Optional
from ..core.control_schema import AgentResult

class ToolGuard:
    @classmethod
    def validate_agent_result(cls, result: AgentResult) -> bool:
        if not result or not isinstance(result, AgentResult):
            raise ValueError("AGENT_RESULT_INVALID: Malformed result object.")

        if not result.is_valid:
            raise ValueError(f"AGENT_RESULT_INVALID: Agent '{result.agent_id}' returned invalid status: {result.error_message}")

        if not result.outputs and result.status.value != "COMPLETED":
            raise ValueError(f"AGENT_RESULT_INVALID: Agent '{result.agent_id}' produced empty output.")

        return True
