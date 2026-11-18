"""Pipeline abstraction for cooking, staging, and packaging across target platforms."""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uaf.golden_slice.manifest.models import PlatformType, GoldenSliceManifest
from uaf.golden_slice.packaging.manifest import ArtifactEntry, ArtifactManifest, BuildManifest


@dataclass
class CookValidationResult:
    is_valid: bool
    missing_assets: List[str] = field(default_factory=list)
    editor_dependencies: List[str] = field(default_factory=list)
    uncooked_references: List[str] = field(default_factory=list)


@dataclass
class PackageResult:
    is_success: bool
    platform: PlatformType
    build_manifest: BuildManifest
    artifact_manifest: ArtifactManifest
    cook_validation: CookValidationResult
    errors: List[str] = field(default_factory=list)


class SlicePackager:
    """Orchestrates cook validation, staging, and packaging for target platforms."""

    def package(
        self,
        manifest: GoldenSliceManifest,
        simulated_asset_paths: Optional[List[str]] = None,
    ) -> PackageResult:
        platform = manifest.target_platform
        build_mnf = BuildManifest(
            engine_version=manifest.engine_version,
            uaf_version=manifest.uaf_version,
            bridge_version=manifest.bridge_version,
            platform=platform.value,
        )
        artifact_mnf = ArtifactManifest(build_id=build_mnf.build_id)

        # 1. Validate Cooking Constraints (Section 65)
        cook_val = self._validate_cooking(simulated_asset_paths or [])
        if not cook_val.is_valid:
            return PackageResult(
                is_success=False,
                platform=platform,
                build_manifest=build_mnf,
                artifact_manifest=artifact_mnf,
                cook_validation=cook_val,
                errors=["Cook validation failed due to missing or uncooked assets."],
            )

        # 2. Stage and Package Output Binaries & Manifests
        exe_name = f"{manifest.project_id}.exe" if platform == PlatformType.WINDOWS else manifest.project_id
        dummy_exe = f"BINARY_PAYLOAD_FOR_{exe_name}_{manifest.version}".encode("utf-8")
        dummy_pak = f"PAK_DATA_FOR_{manifest.project_id}_CONTENT".encode("utf-8")

        artifact_mnf.add_artifact(f"Binaries/{exe_name}", "executable", dummy_exe)
        artifact_mnf.add_artifact(f"Content/Paks/{manifest.project_id}.pak", "package", dummy_pak)

        # Compute combined binary hash
        build_mnf.binary_hash = hashlib.sha256(dummy_exe + dummy_pak).hexdigest()
        build_mnf.content_hash = hashlib.sha256(dummy_pak).hexdigest()

        return PackageResult(
            is_success=True,
            platform=platform,
            build_manifest=build_mnf,
            artifact_manifest=artifact_mnf,
            cook_validation=cook_val,
        )

    def _validate_cooking(self, asset_paths: List[str]) -> CookValidationResult:
        missing: List[str] = []
        editor_deps: List[str] = []
        uncooked: List[str] = []

        for p in asset_paths:
            if "EditorOnly" in p:
                editor_deps.append(p)
            if "Uncooked" in p:
                uncooked.append(p)

        is_valid = len(missing) == 0 and len(editor_deps) == 0 and len(uncooked) == 0
        return CookValidationResult(
            is_valid=is_valid,
            missing_assets=missing,
            editor_dependencies=editor_deps,
            uncooked_references=uncooked,
        )
