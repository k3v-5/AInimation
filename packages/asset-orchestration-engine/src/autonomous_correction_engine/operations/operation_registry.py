from typing import Dict, Optional
from ..core.correction_types import OperationType
from .base_operation import ICorrectionOperation
from .parameter_operation import ParameterUpdateOperation
from .component_operation import ComponentResizeOperation

class CorrectionOperationRegistry:
    def __init__(self):
        self._operations: Dict[OperationType, ICorrectionOperation] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(ParameterUpdateOperation())
        self.register(ComponentResizeOperation())

    def register(self, op: ICorrectionOperation):
        self._operations[op.operation_type] = op

    def get(self, op_type: OperationType) -> Optional[ICorrectionOperation]:
        return self._operations.get(op_type, self._operations.get(OperationType.PARAMETER_UPDATE))
