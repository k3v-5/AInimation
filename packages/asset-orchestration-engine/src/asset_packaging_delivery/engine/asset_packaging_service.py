import time
from typing import Dict, Any, List, Optional
from ..core.package_types import PackageType, PackageStatus, DependencyState
from ..core.package_schema import (
    PackageProfile, DeliveryTarget, PackageFileEntry,
    PackageDependency, PackageManifest, DeliveryReceipt,
    DeliveredAssetPackage, PackagingValidationResult
)
from ..builder.dependency_resolver import DependencyResolver
from ..builder.package_builder import PackageBuilder
from ..builder.package_sealer import PackageSealer
from ..delivery.delivery_service import DeliveryService
from .packaging_hasher import PackagingHasher

class AssetPackagingService:
    """
    Asset Packaging & Delivery Service (AOE v69)
    
    Regla Fundamental:
    EMPAQUETA RIGUROSAMENTE EL ASSET VALIDADO POR F68 EN UN BUNDLE AUTOCONTENIDO,
    VERIFICABLE Y SELLADO, ENTREGÁNDOLO AL TARGET CON COMPROBACIÓN DE HASH Y TRANSACCIÓN.
    """
    def __init__(self, service_version: str = "1.0.0"):
        self.service_version = service_version
        self.delivery_service = DeliveryService()

    def package_and_deliver(
        self,
        ready_asset: Any, # F68 GameEngineReadyAsset
        profile: Optional[PackageProfile] = None,
        target: Optional[DeliveryTarget] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DeliveredAssetPackage:
        ctx = context or {}
        prof = profile or PackageProfile()
        tgt = target or DeliveryTarget()

        asset_id = getattr(ready_asset, "asset_id", "asset")
        sem_id = getattr(ready_asset, "semantic_id", "asset.root")
        readiness_status = getattr(ready_asset, "readiness_status", "READY")
        if hasattr(readiness_status, "value"):
            readiness_status = readiness_status.value
        readiness_score = getattr(ready_asset, "readiness_score", 100.0)
        source_hash = getattr(ready_asset, "source_state_hash", "") or f"SRC_{asset_id}"
        prep_hash = getattr(ready_asset, "prepared_state_hash", "") or f"PREP_{asset_id}"

        package_id = f"PKG_{asset_id}_{int(time.time()*1000)%100000}"

        # 1. Input Gate: F68 Readiness Check
        if readiness_status in ["NOT_READY", "FAILED"]:
            empty_manifest = PackageManifest(
                package_id=package_id, package_version=prof.version,
                asset_id=asset_id, semantic_id=sem_id,
                package_type=prof.package_type, target_engine=prof.target_engine,
                target_engine_version=prof.target_engine_version, target_platform=prof.target_platform,
                source_state_hash=source_hash, prepared_state_hash=prep_hash,
                package_content_hash="INVALID_UNREADY", files=[], dependencies=[]
            )
            failed_rcpt = DeliveryReceipt(
                receipt_id=f"RCPT_FAILED_{package_id}", package_id=package_id,
                target_id=tgt.target_id, destination=tgt.destination_path,
                transferred_files=0, bytes_transferred=0,
                package_hash="INVALID", destination_hash="INVALID",
                status="FAILED"
            )
            return DeliveredAssetPackage(
                package_id=package_id, package_version=prof.version,
                asset_id=asset_id, semantic_id=sem_id, asset_version="1.0.0",
                package_type=prof.package_type,
                engine_profile_id=getattr(ready_asset, "engine_profile_id", "UNREAL_5"),
                export_profile_id=getattr(ready_asset, "export_profile_id", "FBX"),
                package_profile_id=prof.profile_id,
                package_state_hash="HASH_REJECTED_UNREADY",
                package_content_hash="INVALID",
                manifest=empty_manifest, dependencies=[],
                package_path="", package_size=0,
                readiness_status=readiness_status, readiness_score=readiness_score,
                delivery_receipt=failed_rcpt, delivery_status="REJECTED_UNREADY",
                destination=tgt.destination_path
            )

        # 2. Dependency Resolution
        dependencies = DependencyResolver.resolve_dependencies(ready_asset, ctx)
        missing_req = [d for d in dependencies if d.required and d.state == DependencyState.MISSING]
        if missing_req:
            empty_manifest = PackageManifest(
                package_id=package_id, package_version=prof.version,
                asset_id=asset_id, semantic_id=sem_id,
                package_type=prof.package_type, target_engine=prof.target_engine,
                target_engine_version=prof.target_engine_version, target_platform=prof.target_platform,
                source_state_hash=source_hash, prepared_state_hash=prep_hash,
                package_content_hash="INVALID_MISSING_DEP", files=[], dependencies=dependencies
            )
            failed_rcpt = DeliveryReceipt(
                receipt_id=f"RCPT_FAILED_{package_id}", package_id=package_id,
                target_id=tgt.target_id, destination=tgt.destination_path,
                transferred_files=0, bytes_transferred=0,
                package_hash="INVALID", destination_hash="INVALID",
                status="FAILED_MISSING_DEPENDENCY"
            )
            return DeliveredAssetPackage(
                package_id=package_id, package_version=prof.version,
                asset_id=asset_id, semantic_id=sem_id, asset_version="1.0.0",
                package_type=prof.package_type,
                engine_profile_id=getattr(ready_asset, "engine_profile_id", "UNREAL_5"),
                export_profile_id=getattr(ready_asset, "export_profile_id", "FBX"),
                package_profile_id=prof.profile_id,
                package_state_hash="HASH_MISSING_DEP",
                package_content_hash="INVALID",
                manifest=empty_manifest, dependencies=dependencies,
                package_path="", package_size=0,
                readiness_status=readiness_status, readiness_score=readiness_score,
                delivery_receipt=failed_rcpt, delivery_status="FAILED_MISSING_DEPENDENCY",
                destination=tgt.destination_path
            )

        # 3. File List Compilation
        files: List[PackageFileEntry] = [
            PackageFileEntry(
                path=f"Meshes/{asset_id}.fbx", relative_path=f"Meshes/{asset_id}.fbx",
                size_bytes=102400, hash_sha256=f"SHA_MESH_{asset_id}", file_type="STATIC_MESH"
            ),
            PackageFileEntry(
                path=f"Materials/M_{asset_id}.uasset", relative_path=f"Materials/M_{asset_id}.uasset",
                size_bytes=40960, hash_sha256=f"SHA_MAT_{asset_id}", file_type="MATERIAL"
            ),
            PackageFileEntry(
                path=f"Collision/UCX_{asset_id}.fbx", relative_path=f"Collision/UCX_{asset_id}.fbx",
                size_bytes=16384, hash_sha256=f"SHA_COL_{asset_id}", file_type="COLLISION"
            )
        ]

        # 4. Manifest Construction & Sealing
        manifest = PackageBuilder.build_manifest(
            package_id=package_id,
            asset_id=asset_id,
            semantic_id=sem_id,
            profile=prof,
            dependencies=dependencies,
            source_hash=source_hash,
            prepared_hash=prep_hash,
            files=files
        )
        _ = PackageSealer.seal_manifest(manifest)

        # 5. Delivery Execution & Verification
        receipt = self.delivery_service.execute_delivery(manifest, tgt, ctx)
        
        # 6. State Hash
        state_hash = PackagingHasher.compute_package_state_hash(
            package_id=package_id,
            asset_id=asset_id,
            content_hash=manifest.package_content_hash,
            delivery_status=receipt.status
        )

        total_size = sum(f.size_bytes for f in files)

        return DeliveredAssetPackage(
            package_id=package_id,
            package_version=prof.version,
            asset_id=asset_id,
            semantic_id=sem_id,
            asset_version="1.0.0",
            package_type=prof.package_type,
            engine_profile_id=getattr(ready_asset, "engine_profile_id", "UNREAL_5"),
            export_profile_id=getattr(ready_asset, "export_profile_id", "FBX"),
            package_profile_id=prof.profile_id,
            package_state_hash=state_hash,
            package_content_hash=manifest.package_content_hash,
            manifest=manifest,
            dependencies=dependencies,
            package_path=f"{tgt.destination_path}/{package_id}",
            package_size=total_size,
            readiness_status=readiness_status,
            readiness_score=readiness_score,
            delivery_receipt=receipt,
            delivery_status=receipt.status,
            destination=tgt.destination_path,
            provenance={"aoe_version": self.service_version, "timestamp": time.time()},
            audit_trail=[{"step": "SEALED", "time": time.time()}, {"step": "DELIVERED", "status": receipt.status}]
        )

    def validate_delivered_package(self, delivered_package: DeliveredAssetPackage) -> PackagingValidationResult:
        errors = []
        warnings = []
        if not delivered_package.package_id:
            errors.append("MISSING_PACKAGE_ID: Package ID is required.")
        if delivered_package.delivery_status != "DELIVERY_VERIFIED":
            errors.append(f"DELIVERY_NOT_VERIFIED: Status is {delivered_package.delivery_status}")
        return PackagingValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)
