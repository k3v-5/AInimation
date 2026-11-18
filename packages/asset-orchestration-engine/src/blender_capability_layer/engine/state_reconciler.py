from typing import Dict, Any, Optional
from ..core.capability_types import OperationStatus
from ..core.capability_schema import OperationRequest, OperationResponse
from ..adapters.base_adapter import IBlenderAdapter

class StateReconciler:
    @classmethod
    def reconcile_creation(cls, adapter: IBlenderAdapter, request: OperationRequest) -> OperationResponse:
        obj_id = request.parameters.get("object_id")
        existing_obj = adapter.inspect_object(obj_id) if obj_id else None

        if existing_obj:
            return OperationResponse(
                operation_id=request.operation_id,
                status=OperationStatus.SUCCEEDED,
                result={"reconciled": True, "object_id": obj_id, "semantic_id": existing_obj.semantic_id},
                warnings=[f"Idempotency notice: Object '{obj_id}' already existed in Blender. Reconciled state without duplicate creation."],
                adapter_name="StateReconciler"
            )
        else:
            # Seguro ejecutar creación
            return adapter.execute(request)
