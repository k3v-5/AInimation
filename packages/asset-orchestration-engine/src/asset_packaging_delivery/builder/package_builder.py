import time
from typing import Dict, Any, List
from ..core.package_types import PackageType
from ..core.package_schema import (
    PackageProfile, PackageFileEntry, PackageDependency,
    PackageContentManifest, PackageManifest
)
from .package_sealer import PackageSealer

class PackageBuilder:
    @classmethod
    def build_manifest(
        cls,
        package_id: str,
        asset_id: str,
        semantic_id: str,
        profile: PackageProfile,
        dependencies: List[PackageDependency],
        source_hash: str,
        prepared_hash: str,
        files: List[PackageFileEntry]
    ) -> PackageManifest:
        content_hash = PackageSealer.compute_content_hash(files)
        
        manifest = PackageManifest(
            package_id=package_id,
            package_version=profile.version,
            asset_id=asset_id,
            semantic_id=semantic_id,
            package_type=profile.package_type,
            target_engine=profile.target_engine,
            target_engine_version=profile.target_engine_version,
            target_platform=profile.target_platform,
            source_state_hash=source_hash,
            prepared_state_hash=prepared_hash,
            package_content_hash=content_hash,
            files=files,
            dependencies=dependencies,
            schema_version="1.0.0",
            created_at=time.time()
        )

        return manifest
