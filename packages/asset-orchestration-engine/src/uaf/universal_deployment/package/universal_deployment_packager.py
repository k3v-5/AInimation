"""
Universal Deployment Packager (UAF-81.63).
Generates Unreal Engine 5 UnrealPak manifests, IoStore container configurations,
chunking assignment tables, and certified distribution deliverables.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models import DeploymentPackage, PackageManifest


@dataclass
class ProductionReadyDeployment:
    """Production deliverable bundle ready for Unreal Engine 5 cooking and deployment."""
    package_id: str
    created_at: float
    manifest_payload: Dict[str, Any]
    ue5_unrealpak_response_file: str
    ue5_iostore_manifest: str
    ue5_packaging_ini: str
    cryptographic_signatures: Dict[str, str]
    is_certified: bool = True


class UniversalDeploymentPackager:
    """
    Translates deployment packages into Unreal Engine 5 packaging and distribution pipelines.
    """

    def generate_unrealpak_response_file(self, package: DeploymentPackage, mount_point: str = "../../../Game/") -> str:
        """Generates UnrealPak response file mapping local relative files to UE5 mount points."""
        lines = []
        for f in package.manifest.files:
            lines.append(f'"{f.relative_path}" "{mount_point}{f.relative_path}"')
        return "\n".join(lines)

    def generate_iostore_manifest(self, package: DeploymentPackage) -> str:
        """Generates Unreal Engine 5 IoStore container manifest (JSON representation)."""
        data = {
            "ContainerId": package.package_id,
            "ChunkCount": len(package.chunks) if package.chunks else len(package.manifest.files),
            "CompressionMethod": "Oodle",
            "EncryptionMethod": "AES256",
            "Entries": [
                {
                    "Path": f.relative_path,
                    "Size": f.size_bytes,
                    "Hash": f.hash_sha256,
                    "ChunkId": f.chunk_id or f"chunk_{idx}",
                }
                for idx, f in enumerate(package.manifest.files)
            ],
        }
        return json.dumps(data, indent=4)

    def generate_packaging_ini(self) -> str:
        """Generates standard UE5 DefaultEngine.ini chunking configuration."""
        return """[/Script/UnrealEd.ProjectPackagingSettings]
bShareMaterialShaderCode=True
bSharedMaterialNativeLibraries=True
bChunkGeneratedPaks=True
bGenerateChunks=True
bUseIoStore=True
bCookAll=False
"""

    def package_deliverable(self, package: DeploymentPackage) -> ProductionReadyDeployment:
        """Assembles a certified UE5 production deployment deliverable."""
        now = time.time()
        m_payload = {
            "product_id": package.manifest.product_id,
            "content_id": package.manifest.content_id,
            "content_version": package.manifest.content_version,
            "platform": package.manifest.platform,
            "architecture": package.manifest.architecture,
            "file_count": len(package.manifest.files),
            "manifest_hash": package.manifest.calculate_manifest_hash(),
        }

        sigs = dict(package.manifest.signatures)
        if package.signature:
            sigs["primary"] = package.signature

        return ProductionReadyDeployment(
            package_id=package.package_id,
            created_at=now,
            manifest_payload=m_payload,
            ue5_unrealpak_response_file=self.generate_unrealpak_response_file(package),
            ue5_iostore_manifest=self.generate_iostore_manifest(package),
            ue5_packaging_ini=self.generate_packaging_ini(),
            cryptographic_signatures=sigs,
            is_certified=package.is_certified,
        )
