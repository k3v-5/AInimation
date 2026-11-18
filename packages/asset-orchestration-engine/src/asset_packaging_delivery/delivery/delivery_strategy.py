from abc import ABC, abstractmethod
from typing import Dict, Any
from ..core.package_schema import DeliveryTarget, PackageManifest, DeliveryReceipt

class IDeliveryStrategy(ABC):
    @abstractmethod
    def deliver_package(
        self,
        manifest: PackageManifest,
        target: DeliveryTarget,
        context: Dict[str, Any]
    ) -> DeliveryReceipt:
        pass
