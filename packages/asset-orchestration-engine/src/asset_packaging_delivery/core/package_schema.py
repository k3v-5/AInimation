from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .package_types import (
    PackageType, PackageStatus, DeliveryTargetType,
    DependencyState, OverwritePolicy, PackagingSeverity
)

@dataclass
class PackageProfile:
    profile_id: str = "UNREAL_DEFAULT_PACKAGE"
    version: str = "1.0.0"
    package_type: PackageType = PackageType.UNREAL_ASSET_PACKAGE
    target_engine: str = "UNREAL_ENGINE"
    target_engine_version: str = "5.4"
    target_platform: str = "PC"
    include_source: bool = False
    include_mesh: bool = True
    include_materials: bool = True
    include_textures: bool = True
    include_collision: bool = True
    include_lods: bool = True
    include_metadata: bool = True
    include_reports: bool = True
    compression: str = "NONE"
    archive_format: str = "FOLDER"

@dataclass
class DeliveryTarget:
    target_id: str = "TARGET_LOCAL"
    target_type: DeliveryTargetType = DeliveryTargetType.LOCAL_DIRECTORY
    destination_path: str = "E:/Darx_Proyect/Saved/Packages"
    overwrite_policy: OverwritePolicy = OverwritePolicy.OVERWRITE

@dataclass
class PackageFileEntry:
    path: str
    relative_path: str
    size_bytes: int
    hash_sha256: str
    file_type: str = "STATIC_MESH"
    role: str = "PRIMARY"
    required: bool = True

@dataclass
class PackageDependency:
    dependency_id: str
    source: str
    dep_type: str
    required: bool
    resolved_path: str
    state: DependencyState = DependencyState.RESOLVED
    hash_sha256: str = ""

@dataclass
class PackageContentManifest:
    files: List[PackageFileEntry] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    dependencies: List[PackageDependency] = field(default_factory=list)
    total_size_bytes: int = 0
    file_count: int = 0

@dataclass
class PackageManifest:
    package_id: str
    package_version: str
    asset_id: str
    semantic_id: str
    package_type: PackageType
    target_engine: str
    target_engine_version: str
    target_platform: str
    source_state_hash: str
    prepared_state_hash: str
    package_content_hash: str
    files: List[PackageFileEntry] = field(default_factory=list)
    dependencies: List[PackageDependency] = field(default_factory=list)
    schema_version: str = "1.0.0"
    created_at: float = 0.0

@dataclass
class DeliveryReceipt:
    receipt_id: str
    package_id: str
    target_id: str
    destination: str
    transferred_files: int
    bytes_transferred: int
    package_hash: str
    destination_hash: str
    status: str = "DELIVERY_VERIFIED"
    started_at: float = 0.0
    completed_at: float = 0.0

@dataclass
class DeliveredAssetPackage:
    package_id: str
    package_version: str
    asset_id: str
    semantic_id: str
    asset_version: str
    package_type: PackageType
    engine_profile_id: str
    export_profile_id: str
    package_profile_id: str
    package_state_hash: str
    package_content_hash: str
    manifest: PackageManifest
    dependencies: List[PackageDependency]
    package_path: str
    package_size: int
    readiness_status: str
    readiness_score: float
    delivery_receipt: DeliveryReceipt
    delivery_status: str = "DELIVERED"
    destination: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PackagingValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
