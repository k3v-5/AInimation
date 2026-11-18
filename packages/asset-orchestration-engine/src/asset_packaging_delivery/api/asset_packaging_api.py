from typing import Dict, Any, List, Optional
from ..core.package_types import (
    PackageType, PackageStatus, DeliveryTargetType,
    DependencyState, OverwritePolicy, PackagingSeverity
)
from ..core.package_schema import (
    PackageProfile, DeliveryTarget, PackageFileEntry,
    PackageDependency, PackageManifest, DeliveryReceipt,
    DeliveredAssetPackage, PackagingValidationResult
)
from ..engine.asset_packaging_service import AssetPackagingService

class AssetPackagingAPI:
    """
    Asset Packaging API (AOE v69)
    
    Regla Fundamental:
    EMPAQUETA RIGUROSAMENTE EL ASSET VALIDADO POR F68 EN UN BUNDLE AUTOCONTENIDO,
    VERIFICABLE Y SELLADO, ENTREGÁNDOLO AL TARGET CON COMPROBACIÓN DE HASH Y TRANSACCIÓN.
    """
    def __init__(self, service_version: str = "1.0.0"):
        self._service = AssetPackagingService(service_version=service_version)

    def package_and_deliver_asset(
        self,
        ready_asset: Any,
        profile: Optional[PackageProfile] = None,
        target: Optional[DeliveryTarget] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DeliveredAssetPackage:
        return self._service.package_and_deliver(
            ready_asset, profile, target, context
        )

    def validate_delivered_package(self, delivered_package: DeliveredAssetPackage) -> PackagingValidationResult:
        return self._service.validate_delivered_package(delivered_package)
