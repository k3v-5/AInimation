"""
CapabilityRegistry manages discovery of engine capabilities.
UAF-81.0 Section 52.
"""

from typing import List, Optional, Union
from ..contracts.registry import BaseRegistry
from .capability_description import CapabilityDescription
from ..core.identity.asset_types import AssetType
from ..core.operations.operation_types import OperationType


class CapabilityRegistry(BaseRegistry[CapabilityDescription]):
    """
    Registry allowing the engine to answer:
    - What can this system produce?
    - Which generator supports this asset type?
    - Which backend can execute this operation?
    """
    def __init__(self):
        super().__init__(name="CapabilityRegistry")

    def register_capability(self, capability: CapabilityDescription) -> None:
        self.register(capability.capability_id, capability, overwrite=True)

    def find_for_asset(
        self,
        asset_type: Union[AssetType, str],
        operation_type: Optional[Union[OperationType, str]] = None,
        target: Optional[str] = None,
    ) -> List[CapabilityDescription]:
        """Find all capabilities supporting the given asset type and constraints."""
        at = AssetType.from_str(asset_type) if isinstance(asset_type, str) else asset_type
        op = OperationType.from_str(operation_type) if isinstance(operation_type, str) and operation_type else operation_type

        def matches(cap: CapabilityDescription) -> bool:
            if not cap.supports_asset_type(at):
                return False
            if op and not cap.supports_operation(op):
                return False
            if target and not cap.supports_target(target):
                return False
            return True

        return self.find(matches)

    def can_produce(self, asset_type: Union[AssetType, str], target: Optional[str] = None) -> bool:
        """Query if any registered capability can generate the given asset type."""
        caps = self.find_for_asset(asset_type, operation_type=OperationType.GENERATE, target=target)
        return len(caps) > 0
