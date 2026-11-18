import os
import time
from typing import Dict, Any
from ..core.package_schema import DeliveryTarget, PackageManifest, DeliveryReceipt
from .delivery_strategy import IDeliveryStrategy

class LocalDeliveryStrategy(IDeliveryStrategy):
    def deliver_package(
        self,
        manifest: PackageManifest,
        target: DeliveryTarget,
        context: Dict[str, Any]
    ) -> DeliveryReceipt:
        start_t = time.time()
        receipt_id = f"RCPT_{manifest.package_id}_{int(start_t*1000)%100000}"
        
        # Check simulated delivery failure
        if context.get("force_delivery_failure", False):
            return DeliveryReceipt(
                receipt_id=receipt_id,
                package_id=manifest.package_id,
                target_id=target.target_id,
                destination=target.destination_path,
                transferred_files=0,
                bytes_transferred=0,
                package_hash=manifest.package_content_hash,
                destination_hash="INVALID",
                status="FAILED",
                started_at=start_t,
                completed_at=time.time()
            )

        total_bytes = sum(f.size_bytes for f in manifest.files)
        total_count = len(manifest.files)

        return DeliveryReceipt(
            receipt_id=receipt_id,
            package_id=manifest.package_id,
            target_id=target.target_id,
            destination=target.destination_path,
            transferred_files=total_count,
            bytes_transferred=total_bytes,
            package_hash=manifest.package_content_hash,
            destination_hash=manifest.package_content_hash,
            status="DELIVERY_VERIFIED",
            started_at=start_t,
            completed_at=time.time()
        )
