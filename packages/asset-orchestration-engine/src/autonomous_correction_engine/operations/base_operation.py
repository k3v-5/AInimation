from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from ..core.correction_types import OperationType, ActionAuthorization
from ..core.correction_schema import ParameterChange

class ICorrectionOperation(ABC):
    @property
    @abstractmethod
    def operation_type(self) -> OperationType:
        pass

    @abstractmethod
    def validate_action(self, action: Any, current_state: Dict[str, Any]) -> Tuple[bool, ActionAuthorization, str]:
        pass

    @abstractmethod
    def apply_action(self, action: Any, current_state: Dict[str, Any]) -> Tuple[bool, ParameterChange, Dict[str, Any]]:
        pass
