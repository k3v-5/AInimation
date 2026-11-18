from typing import Dict, Any, List, Optional
from ...core.capability_types import OperationStatus
from ...core.capability_schema import (
    OperationRequest, OperationResponse, BlenderSceneState, BlenderObjectState
)
from ..base_adapter import IBlenderAdapter
from ..mock_adapter import MockBlenderAdapter
from .ahujasid_translator import AhujasidCommandTranslator, AhujasidResponseTranslator

class AhujasidBlenderAdapter(IBlenderAdapter):
    def __init__(self, backend: Optional[MockBlenderAdapter] = None):
        self._backend = backend or MockBlenderAdapter()
        self.is_connected = True

    def connect(self) -> bool:
        self.is_connected = True
        return self._backend.connect()

    def disconnect(self) -> bool:
        self.is_connected = False
        return self._backend.disconnect()

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.is_connected else "UNAVAILABLE",
            "latency_ms": 2.5,
            "adapter": "AhujasidBlenderAdapter"
        }

    def supported_capabilities(self) -> List[str]:
        return self._backend.supported_capabilities()

    def execute(self, request: OperationRequest) -> OperationResponse:
        if not self.is_connected:
            return OperationResponse(
                operation_id=request.operation_id,
                status=OperationStatus.FAILED,
                errors=["CONNECTION_ERROR: Ahujasid MCP is not connected."],
                adapter_name="AhujasidBlenderAdapter"
            )

        # 1. Traducir request a MCP
        mcp_cmd = AhujasidCommandTranslator.to_mcp_command(request)
        
        # 2. Ejecutar sobre backend
        backend_res = self._backend.execute(request)
        
        # 3. Traducir respuesta
        mcp_raw = {
            "status": "SUCCESS" if backend_res.status == OperationStatus.SUCCEEDED else "FAILED",
            "result": backend_res.result,
            "errors": backend_res.errors,
            "warnings": backend_res.warnings
        }
        translated = AhujasidResponseTranslator.from_mcp_response(request.operation_id, mcp_raw)
        return translated

    def inspect_object(self, object_id: str) -> Optional[BlenderObjectState]:
        return self._backend.inspect_object(object_id)

    def inspect_scene(self) -> BlenderSceneState:
        return self._backend.inspect_scene()
