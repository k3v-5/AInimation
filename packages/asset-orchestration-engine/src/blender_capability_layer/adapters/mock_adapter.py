import time
from typing import Dict, Any, List, Optional
from ..core.capability_types import OperationStatus
from ..core.capability_schema import (
    OperationRequest, OperationResponse, BlenderSceneState, BlenderObjectState
)
from .base_adapter import IBlenderAdapter

class MockBlenderAdapter(IBlenderAdapter):
    def __init__(self):
        self.is_connected = True
        self.scene = BlenderSceneState(scene_id="SCENE_MOCK")
        self.fault_connection_loss = False
        self.fault_timeout = False
        self.executed_operations_count = 0

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.is_connected and not self.fault_connection_loss else "UNAVAILABLE",
            "latency_ms": 1.2
        }

    def supported_capabilities(self) -> List[str]:
        return [
            "object.create", "geometry.create", "transform.set",
            "modifier.add", "material.create", "material.assign",
            "object.inspect", "scene.inspect", "object.delete", "export.fbx"
        ]

    def execute(self, request: OperationRequest) -> OperationResponse:
        self.executed_operations_count += 1

        if self.fault_connection_loss:
            return OperationResponse(
                operation_id=request.operation_id,
                status=OperationStatus.FAILED,
                errors=["CONNECTION_ERROR: Lost connection to Blender MCP."],
                adapter_name="MockBlenderAdapter"
            )

        if self.fault_timeout:
            return OperationResponse(
                operation_id=request.operation_id,
                status=OperationStatus.TIMEOUT,
                errors=["TIMEOUT: Operation exceeded allocated execution time."],
                adapter_name="MockBlenderAdapter"
            )

        if request.is_dry_run:
            return OperationResponse(
                operation_id=request.operation_id,
                status=OperationStatus.SUCCEEDED,
                result={"dry_run": True, "target": request.parameters.get("object_id", "GLOBAL")},
                adapter_name="MockBlenderAdapter"
            )

        cap = request.capability_id
        params = request.parameters

        if cap == "object.create":
            obj_id = params.get("object_id", f"OBJ_{len(self.scene.objects)+1}")
            sem_id = params.get("semantic_id", obj_id.lower())
            name = params.get("name", obj_id)
            obj = BlenderObjectState(object_id=obj_id, semantic_id=sem_id, name=name)
            self.scene.objects[obj_id] = obj
            self.scene.revision += 1
            return OperationResponse(
                operation_id=request.operation_id,
                status=OperationStatus.SUCCEEDED,
                result={"created_object_id": obj_id, "semantic_id": sem_id},
                adapter_name="MockBlenderAdapter"
            )

        elif cap == "transform.set":
            obj_id = params.get("object_id")
            if obj_id in self.scene.objects:
                if "scale" in params:
                    self.scene.objects[obj_id].transform["scale"] = params["scale"]
                if "location" in params:
                    self.scene.objects[obj_id].transform["location"] = params["location"]
                self.scene.revision += 1
                return OperationResponse(
                    operation_id=request.operation_id,
                    status=OperationStatus.SUCCEEDED,
                    result={"updated_object_id": obj_id},
                    adapter_name="MockBlenderAdapter"
                )
            else:
                return OperationResponse(
                    operation_id=request.operation_id,
                    status=OperationStatus.FAILED,
                    errors=[f"Object '{obj_id}' not found in scene."],
                    adapter_name="MockBlenderAdapter"
                )

        elif cap == "material.assign":
            obj_id = params.get("object_id")
            mat_name = params.get("material_name", "DEFAULT_MAT")
            if obj_id in self.scene.objects:
                self.scene.objects[obj_id].materials.append(mat_name)
                self.scene.revision += 1
                return OperationResponse(
                    operation_id=request.operation_id,
                    status=OperationStatus.SUCCEEDED,
                    result={"assigned_material": mat_name},
                    adapter_name="MockBlenderAdapter"
                )

        elif cap == "object.delete":
            obj_id = params.get("object_id")
            if obj_id in self.scene.objects:
                del self.scene.objects[obj_id]
                self.scene.revision += 1
                return OperationResponse(
                    operation_id=request.operation_id,
                    status=OperationStatus.SUCCEEDED,
                    result={"deleted_object_id": obj_id},
                    adapter_name="MockBlenderAdapter"
                )

        return OperationResponse(
            operation_id=request.operation_id,
            status=OperationStatus.SUCCEEDED,
            result={"status": "OK"},
            adapter_name="MockBlenderAdapter"
        )

    def inspect_object(self, object_id: str) -> Optional[BlenderObjectState]:
        return self.scene.objects.get(object_id)

    def inspect_scene(self) -> BlenderSceneState:
        return self.scene
