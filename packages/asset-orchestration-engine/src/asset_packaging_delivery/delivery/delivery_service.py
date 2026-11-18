from typing import Dict, Any, Optional
from ..core.package_schema import DeliveryTarget, PackageManifest, DeliveryReceipt
from .delivery_strategy import IDeliveryStrategy
from .local_delivery_strategy import LocalDeliveryStrategy

class DeliveryService:
    def __init__(self):
        self._strategy: IDeliveryStrategy = LocalDeliveryStrategy()

    def execute_delivery(
        self,
        manifest: PackageManifest,
        target: Optional[DeliveryTarget] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DeliveryReceipt:
        tgt = target or DeliveryTarget()
        ctx = context or {}
        return self._strategy.deliver_package(manifest, tgt, ctx)
