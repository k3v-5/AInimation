from typing import Dict, Any, Optional
from ...core.capability_types import OperationStatus
from ...core.capability_schema import OperationRequest, OperationResponse

class AhujasidCommandTranslator:
    @classmethod
    def to_mcp_command(cls, request: OperationRequest) -> Dict[str, Any]:
        return {
            "server": "AhujasidMCP",
            "tool": f"blender_{request.capability_id.replace('.', '_')}",
            "arguments": request.parameters,
            "timeout": request.timeout_sec
        }

class AhujasidResponseTranslator:
    @classmethod
    def from_mcp_response(cls, operation_id: str, mcp_raw_response: Dict[str, Any]) -> OperationResponse:
        status_raw = mcp_raw_response.get("status", "SUCCESS")
        status = OperationStatus.SUCCEEDED if status_raw == "SUCCESS" else OperationStatus.FAILED
        
        return OperationResponse(
            operation_id=operation_id,
            status=status,
            result=mcp_raw_response.get("result", {}),
            errors=mcp_raw_response.get("errors", []),
            warnings=mcp_raw_response.get("warnings", []),
            adapter_name="AhujasidBlenderAdapter"
        )
