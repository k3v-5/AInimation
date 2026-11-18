from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..core.capability_schema import OperationRequest, OperationResponse, BlenderSceneState, BlenderObjectState

class IBlenderAdapter(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def supported_capabilities(self) -> List[str]:
        pass

    @abstractmethod
    def execute(self, request: OperationRequest) -> OperationResponse:
        pass

    @abstractmethod
    def inspect_object(self, object_id: str) -> Optional[BlenderObjectState]:
        pass

    @abstractmethod
    def inspect_scene(self) -> BlenderSceneState:
        pass
