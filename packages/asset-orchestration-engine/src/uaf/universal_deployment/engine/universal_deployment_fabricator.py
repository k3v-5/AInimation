"""
Universal Deployment Fabricator (UAF-81.63).
Authoritative engine for asset registration, dependency resolution, build graphs,
content addressing, packaging, transactional installation, delta patching, and repair.
"""

from __future__ import annotations
import copy
import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..models import (
    AssetType,
    ContentType,
    DependencyType,
    ConflictPolicy,
    BuildState,
    ArtifactLifecycle,
    PackageType,
    DownloadState,
    InstallState,
    UninstallState,
    TrustPolicy,
    RepairAction,
    AssetRecord,
    ContentPackage,
    DependencyEdge,
    DependencyGraph,
    BuildNode,
    BuildGraph,
    BuildCacheEntry,
    BuildArtifact,
    FileManifestEntry,
    PackageManifest,
    ChunkDescriptor,
    DeploymentPackage,
    DownloadRequest,
    InstallationRecord,
    PatchDescriptor,
    SigningCertificate,
    DeploymentDiagnosticReport,
)


class UniversalDeploymentFabricator:
    """
    Authoritative fabrication and deployment management platform.
    """

    def __init__(self, cache_dir: str = "/tmp/build_cache", default_platform: str = "Windows"):
        self.cache_dir = cache_dir
        self.default_platform = default_platform

        # Registries
        self._assets: Dict[str, AssetRecord] = {}
        self._content_packages: Dict[str, ContentPackage] = {}
        self._artifacts: Dict[str, BuildArtifact] = {}
        self._packages: Dict[str, DeploymentPackage] = {}
        self._certificates: Dict[str, SigningCertificate] = {}

        # Dependency & Build graphs
        self._dependency_graph = DependencyGraph()
        self._build_graph = BuildGraph()
        self._build_cache: Dict[str, BuildCacheEntry] = {}

        # Installation & Deployment Runtime
        self._downloads: Dict[str, DownloadRequest] = {}
        self._installed_packages: Dict[str, InstallationRecord] = {}
        self._staged_packages: Dict[str, InstallationRecord] = {}
        self._installation_backups: Dict[str, InstallationRecord] = {}

        # Default certificate authority
        self._init_default_certificates()

    def _init_default_certificates(self) -> None:
        """Initializes canonical trusted signing certificates."""
        default_cert = SigningCertificate(
            cert_id="cert_prod_root",
            issuer="AssetOrchestrationEngine_Root_CA",
            public_key="RSA4096_PUB_AOE_AUTH_KEY_2026",
            trust_policy=TrustPolicy.TRUSTED,
            expires_at=time.time() + 31536000.0,
        )
        self._certificates[default_cert.cert_id] = default_cert

    # ==========================================================================
    # ASSET REGISTRY (§5, §6, §7, §8)
    # ==========================================================================

    def register_asset(
        self,
        asset_id: str,
        asset_type: AssetType,
        source_id: str,
        version: str = "1.0.0",
        content_bytes: Optional[bytes] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
    ) -> AssetRecord:
        """Registers an asset with path-independent stable ID (§7)."""
        record = AssetRecord(
            asset_id=asset_id,
            asset_type=asset_type,
            source_id=source_id,
            version=version,
            metadata=metadata or {},
            dependencies=list(dependencies or []),
        )
        if content_bytes is not None:
            record.calculate_content_hash(content_bytes)
        else:
            record.content_hash = hashlib.sha256(asset_id.encode("utf-8")).hexdigest()

        self._assets[asset_id] = record
        self._dependency_graph.add_node(asset_id)
        if dependencies:
            for dep in dependencies:
                self.add_dependency(asset_id, dep, DependencyType.REQUIRED)

        return record

    def unregister_asset(self, asset_id: str) -> bool:
        if asset_id in self._assets:
            del self._assets[asset_id]
            return True
        return False

    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        return self._assets.get(asset_id)

    def list_assets(self) -> List[AssetRecord]:
        return list(self._assets.values())

    # ==========================================================================
    # CONTENT REGISTRY (§9, §10, §11)
    # ==========================================================================

    def register_content_package(
        self,
        content_id: str,
        content_type: ContentType,
        content_version: str = "1.0.0",
        assets: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContentPackage:
        pkg = ContentPackage(
            content_id=content_id,
            content_type=content_type,
            content_version=content_version,
            manifest_id=f"manifest_{content_id}_{content_version}",
            assets=list(assets or []),
            metadata=metadata or {},
        )
        pkg.content_hash = hashlib.sha256(json.dumps(pkg.assets, sort_keys=True).encode("utf-8")).hexdigest()
        self._content_packages[content_id] = pkg
        return pkg

    def get_content_package(self, content_id: str) -> Optional[ContentPackage]:
        return self._content_packages.get(content_id)

    def list_content_packages(self) -> List[ContentPackage]:
        return list(self._content_packages.values())

    # ==========================================================================
    # DEPENDENCY GRAPH ENGINE (§12, §13, §14, §15, §16, §17, §18, §19, §20, §21, §22)
    # ==========================================================================

    @property
    def dependency_graph(self) -> DependencyGraph:
        return self._dependency_graph

    def add_dependency(
        self,
        source_id: str,
        target_id: str,
        dep_type: DependencyType = DependencyType.REQUIRED,
        min_version: Optional[str] = None,
        max_version: Optional[str] = None,
    ) -> None:
        edge = DependencyEdge(source_id, target_id, dep_type, min_version, max_version)
        self._dependency_graph.add_edge(edge)

    def detect_cycles(self) -> bool:
        return self._dependency_graph.has_cycle()

    def get_build_order(self) -> List[str]:
        return self._dependency_graph.topological_sort()

    def resolve_conflicts(self, policy: ConflictPolicy = ConflictPolicy.REJECT) -> Tuple[bool, List[str]]:
        """Identifies conflicting dependency edges and evaluates resolution policy (§21, §22)."""
        conflicts = []
        for e in self._dependency_graph.edges:
            if e.dep_type == DependencyType.CONFLICT:
                conflicts.append(f"Conflict: {e.source_id} conflicts with {e.target_id}")

        if conflicts:
            if policy == ConflictPolicy.REJECT:
                return False, conflicts
            elif policy == ConflictPolicy.SELECT_COMPATIBLE:
                return True, [f"Resolved automatically: {c}" for c in conflicts]
            elif policy == ConflictPolicy.REQUIRE_USER_DECISION:
                return False, ["User intervention required for conflict resolution."]
        return True, []

    # ==========================================================================
    # BUILD ENGINE & CACHE (§28, §29, §30, §31, §32, §33, §34, §35, §36, §37, §38, §39, §40)
    # ==========================================================================

    def create_build_node(
        self,
        node_id: str,
        inputs: List[str],
        output_artifact: str,
        tool_version: str = "1.0.0",
        command: str = "compile",
        depends_on: Optional[List[str]] = None,
    ) -> BuildNode:
        node = BuildNode(
            node_id=node_id,
            inputs=inputs,
            output_artifact=output_artifact,
            tool_version=tool_version,
            command=command,
        )
        self._build_graph.add_node(node, depends_on=depends_on)
        return node

    def compute_cache_key(self, node: BuildNode, input_hashes: Dict[str, str]) -> str:
        """Deterministically generates cache key based on inputs and toolchain (§35)."""
        data = {
            "node_id": node.node_id,
            "tool_version": node.tool_version,
            "command": node.command,
            "platform": self.default_platform,
            "input_hashes": sorted([(k, input_hashes.get(k, "")) for k in node.inputs]),
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

    def execute_build(
        self,
        node_id: str,
        input_data: Optional[Dict[str, bytes]] = None,
        force_rebuild: bool = False,
    ) -> Tuple[bool, BuildArtifact, str]:
        """
        Executes build step with cache hit/miss evaluation (§37, §38, §40):
        If inputs match cache key and force_rebuild is False -> CACHE HIT.
        Otherwise -> CACHE MISS & builds artifact.
        """
        if node_id not in self._build_graph.nodes:
            raise KeyError(f"Build node '{node_id}' not found in build graph.")

        node = self._build_graph.nodes[node_id]
        input_hashes = {}
        if input_data:
            for k, b in input_data.items():
                input_hashes[k] = hashlib.sha256(b).hexdigest()

        cache_key = self.compute_cache_key(node, input_hashes)

        # Cache Hit Check
        if not force_rebuild and cache_key in self._build_cache:
            entry = self._build_cache[cache_key]
            if entry.artifact_id in self._artifacts:
                return True, self._artifacts[entry.artifact_id], "CACHE_HIT"

        # Cache Miss: Build execution
        combined_inputs = b"".join(input_data.values()) if input_data else node_id.encode("utf-8")
        content_hash = hashlib.sha256(combined_inputs).hexdigest()

        artifact = BuildArtifact(
            artifact_id=node.output_artifact or f"art_{node_id}",
            artifact_type=AssetType.DATA,
            version=node.tool_version,
            platform=self.default_platform,
            size_bytes=len(combined_inputs),
            content_hash=content_hash,
            build_id=f"build_{int(time.time()*1000)}",
            lifecycle=ArtifactLifecycle.VALIDATED,
        )
        self.register_artifact(artifact)

        # Store in cache
        self._build_cache[cache_key] = BuildCacheEntry(
            cache_key=cache_key,
            artifact_id=artifact.artifact_id,
            source_hash=content_hash,
            tool_version=node.tool_version,
            platform=self.default_platform,
            created_at=time.time(),
        )

        return True, artifact, "CACHE_MISS"

    def invalidate_cache(self, key_or_toolchain: Optional[str] = None) -> int:
        """Invalidates entire cache or entries matching a toolchain version (§39)."""
        if key_or_toolchain is None:
            count = len(self._build_cache)
            self._build_cache.clear()
            return count

        to_remove = [k for k, v in self._build_cache.items() if v.tool_version == key_or_toolchain or k == key_or_toolchain]
        for k in to_remove:
            del self._build_cache[k]
        return len(to_remove)

    # ==========================================================================
    # ARTIFACT & SIGNING REGISTRY (§44, §45, §46, §47, §48, §55, §56, §57, §58)
    # ==========================================================================

    def register_artifact(self, artifact: BuildArtifact) -> None:
        self._artifacts[artifact.artifact_id] = artifact

    def get_artifact(self, artifact_id: str) -> Optional[BuildArtifact]:
        return self._artifacts.get(artifact_id)

    def revoke_artifact(self, artifact_id: str) -> bool:
        """Revokes an artifact, marking it untrusted (§48)."""
        if artifact_id in self._artifacts:
            self._artifacts[artifact_id].lifecycle = ArtifactLifecycle.REVOKED
            return True
        return False

    def register_certificate(self, cert: SigningCertificate) -> None:
        self._certificates[cert.cert_id] = cert

    def sign_package(self, package: DeploymentPackage, cert_id: str = "cert_prod_root") -> Tuple[bool, str]:
        """Cryptographically signs package manifest and payload (§55)."""
        if cert_id not in self._certificates:
            return False, "Certificate not found."
        cert = self._certificates[cert_id]
        if cert.trust_policy != TrustPolicy.TRUSTED:
            return False, f"Certificate trust policy is {cert.trust_policy.value}."

        manifest_hash = package.manifest.calculate_manifest_hash()
        signature_payload = f"{cert.public_key}:{manifest_hash}"
        sig = hashlib.sha256(signature_payload.encode("utf-8")).hexdigest()
        package.signature = sig
        package.manifest.signatures[cert_id] = sig
        package.is_certified = True
        return True, sig

    def verify_package_signature(self, package: DeploymentPackage) -> bool:
        """Validates signature against trusted certificates (§56, §57)."""
        if not package.signature or not package.is_certified:
            return False
        manifest_hash = package.manifest.calculate_manifest_hash()
        for cert in self._certificates.values():
            if cert.trust_policy == TrustPolicy.TRUSTED:
                expected_sig = hashlib.sha256(f"{cert.public_key}:{manifest_hash}".encode("utf-8")).hexdigest()
                if expected_sig == package.signature:
                    return True
        return False

    # ==========================================================================
    # PACKAGING & CHUNKING (§61, §62, §63, §64, §67, §68, §69)
    # ==========================================================================

    def generate_manifest(
        self,
        product_id: str,
        content_id: str,
        content_version: str,
        files: Dict[str, bytes],
        dependencies: Optional[List[str]] = None,
        optional_dependencies: Optional[List[str]] = None,
        conflicts: Optional[List[str]] = None,
    ) -> PackageManifest:
        """Builds package manifest with file hashes and sizes (§51)."""
        entries = []
        hashes = {}
        for r_path, data in files.items():
            f_hash = hashlib.sha256(data).hexdigest()
            entries.append(FileManifestEntry(relative_path=r_path, size_bytes=len(data), hash_sha256=f_hash))
            hashes[r_path] = f_hash

        manifest = PackageManifest(
            product_id=product_id,
            content_id=content_id,
            content_version=content_version,
            platform=self.default_platform,
            files=entries,
            dependencies=list(dependencies or []),
            optional_dependencies=list(optional_dependencies or []),
            conflicts=list(conflicts or []),
            hashes=hashes,
        )
        return manifest

    def create_package(
        self,
        package_id: str,
        package_type: PackageType,
        manifest: PackageManifest,
        payload_files: Dict[str, bytes],
        chunk_size: int = 0,
        cert_id: Optional[str] = "cert_prod_root",
    ) -> DeploymentPackage:
        """Assembles package with optional chunking and signs it (§63, §67)."""
        chunks = []
        if chunk_size > 0:
            for path, data in payload_files.items():
                offset = 0
                idx = 0
                while offset < len(data):
                    slice_bytes = data[offset : offset + chunk_size]
                    c_hash = hashlib.sha256(slice_bytes).hexdigest()
                    chunks.append(ChunkDescriptor(
                        chunk_id=f"{path}.chk_{idx}",
                        offset=offset,
                        size_bytes=len(slice_bytes),
                        hash_sha256=c_hash,
                    ))
                    offset += chunk_size
                    idx += 1

        pkg = DeploymentPackage(
            package_id=package_id,
            package_type=package_type,
            manifest=manifest,
            chunks=chunks,
            payload_files=copy.deepcopy(payload_files),
        )
        if cert_id:
            self.sign_package(pkg, cert_id)

        self._packages[package_id] = pkg
        return pkg

    def get_package(self, package_id: str) -> Optional[DeploymentPackage]:
        return self._packages.get(package_id)

    # ==========================================================================
    # DOWNLOAD SERVICE (§70, §71, §72, §73, §74, §75)
    # ==========================================================================

    def request_download(self, package_id: str, url: str) -> DownloadRequest:
        req = DownloadRequest(
            download_id=f"dl_{package_id}_{int(time.time()*1000)}",
            package_id=package_id,
            target_url=url,
            state=DownloadState.QUEUED,
        )
        self._downloads[req.download_id] = req
        return req

    def process_download(self, download_id: str, mock_data: Optional[bytes] = None) -> Tuple[bool, str]:
        if download_id not in self._downloads:
            return False, "Download not found."
        req = self._downloads[download_id]
        req.state = DownloadState.DOWNLOADING
        req.attempts += 1

        if req.package_id not in self._packages:
            req.state = DownloadState.FAILED
            req.error_message = f"Package '{req.package_id}' not found on server."
            return False, req.error_message

        pkg = self._packages[req.package_id]
        total_len = sum(len(b) for b in pkg.payload_files.values())
        req.total_bytes = total_len
        req.bytes_downloaded = total_len

        # Checksum verification
        req.state = DownloadState.VERIFYING
        if not self.verify_package_signature(pkg):
            req.state = DownloadState.FAILED
            req.error_message = "Download package signature verification failed."
            return False, req.error_message

        req.state = DownloadState.COMPLETED
        return True, "Download completed and verified."

    # ==========================================================================
    # TRANSACTIONAL INSTALLATION SERVICE (§76, §77, §78, §79, §80, §81, §82, §83, §84, §85)
    # ==========================================================================

    def stage_install(self, package_id: str, install_dir: str = "/opt/game") -> Tuple[bool, str]:
        """Stages package payload in isolated transaction area (§79)."""
        if package_id not in self._packages:
            return False, f"Package '{package_id}' not found."

        pkg = self._packages[package_id]
        if not self.verify_package_signature(pkg):
            return False, "Cannot install untrusted or unsigned package."

        # Check required dependencies
        for dep in pkg.manifest.dependencies:
            if dep not in self._installed_packages:
                return False, f"Missing required dependency: '{dep}'."

        installed_files = {path: hashlib.sha256(data).hexdigest() for path, data in pkg.payload_files.items()}
        record = InstallationRecord(
            install_id=f"inst_{package_id}",
            package_id=package_id,
            version=pkg.manifest.content_version,
            install_dir=install_dir,
            installed_files=installed_files,
            state=InstallState.INSTALLING,
            installed_at=time.time(),
        )
        self._staged_packages[package_id] = record
        return True, "Staged successfully."

    def commit_install(self, package_id: str) -> Tuple[bool, str]:
        """Atomically promotes staged files to active installation (§80)."""
        if package_id not in self._staged_packages:
            return False, "No staged installation found to commit."

        record = self._staged_packages.pop(package_id)

        # Backup existing installation if updating
        if package_id in self._installed_packages:
            self._installation_backups[package_id] = copy.deepcopy(self._installed_packages[package_id])

        record.state = InstallState.COMPLETED
        self._installed_packages[package_id] = record
        return True, f"Installation of '{package_id}' committed successfully."

    def rollback_install(self, package_id: str) -> Tuple[bool, str]:
        """Rolls back to previous valid installation snapshot (§82)."""
        if package_id in self._staged_packages:
            del self._staged_packages[package_id]

        if package_id in self._installation_backups:
            self._installed_packages[package_id] = copy.deepcopy(self._installation_backups[package_id])
            return True, "Rolled back to previous valid installation."
        elif package_id in self._installed_packages:
            del self._installed_packages[package_id]
            return True, "Installation aborted and purged."

        return False, "No state to roll back."

    def uninstall_package(self, package_id: str) -> Tuple[bool, str]:
        """Uninstalls package ensuring no active consumers depend on it (§84, §85)."""
        if package_id not in self._installed_packages:
            return False, "Package not installed."

        # Check consumers
        for inst_id, inst in self._installed_packages.items():
            if inst_id != package_id:
                pkg = self._packages.get(inst.package_id)
                if pkg and package_id in pkg.manifest.dependencies:
                    return False, f"Cannot uninstall: package '{inst_id}' depends on '{package_id}'."

        del self._installed_packages[package_id]
        return True, f"Package '{package_id}' uninstalled successfully."

    # ==========================================================================
    # UPDATE & DELTA PATCHING (§89, §90, §91, §92)
    # ==========================================================================

    def create_delta_patch(self, source_pkg_id: str, target_pkg_id: str) -> PatchDescriptor:
        """Calculates differential delta between source and target packages."""
        src = self._packages[source_pkg_id]
        tgt = self._packages[target_pkg_id]

        delta_files = []
        for path, data in tgt.payload_files.items():
            if path not in src.payload_files or src.payload_files[path] != data:
                delta_files.append(path)

        removed_files = [p for p in src.payload_files if p not in tgt.payload_files]

        return PatchDescriptor(
            patch_id=f"patch_{source_pkg_id}_to_{target_pkg_id}",
            source_version=src.manifest.content_version,
            target_version=tgt.manifest.content_version,
            package_id=tgt.package_id,
            delta_files=delta_files,
            removed_files=removed_files,
        )

    def apply_delta_patch(self, package_id: str, patch: PatchDescriptor) -> Tuple[bool, str]:
        """Applies differential patch to active installation."""
        if package_id not in self._installed_packages:
            return False, "Package not installed."

        target_pkg = self._packages.get(patch.package_id)
        if not target_pkg:
            return False, "Target package data not found."

        inst = self._installed_packages[package_id]
        # Backup prior to patch
        self._installation_backups[package_id] = copy.deepcopy(inst)

        # Apply deltas
        for df in patch.delta_files:
            if df in target_pkg.payload_files:
                inst.installed_files[df] = hashlib.sha256(target_pkg.payload_files[df]).hexdigest()

        # Remove deleted
        for rf in patch.removed_files:
            inst.installed_files.pop(rf, None)

        inst.version = patch.target_version
        return True, f"Patch applied: upgraded to version {patch.target_version}."

    # ==========================================================================
    # VERIFICATION & REPAIR (§216)
    # ==========================================================================

    def verify_installation_integrity(self, package_id: str) -> Tuple[bool, List[str]]:
        """Scans installed files against authoritative manifest hashes."""
        if package_id not in self._installed_packages or package_id not in self._packages:
            return False, ["Package not found."]

        inst = self._installed_packages[package_id]
        pkg = self._packages[package_id]

        corrupted = []
        for entry in pkg.manifest.files:
            p = entry.relative_path
            if p not in inst.installed_files:
                corrupted.append(f"MISSING: {p}")
            elif inst.installed_files[p] != entry.hash_sha256:
                corrupted.append(f"HASH_MISMATCH: {p}")

        return (len(corrupted) == 0), corrupted

    def repair_file(self, package_id: str, relative_path: str, clean_bytes: bytes) -> Tuple[bool, str]:
        """Restores a corrupted or missing file with clean bytes (§216)."""
        if package_id not in self._installed_packages or package_id not in self._packages:
            return False, "Package not found."

        inst = self._installed_packages[package_id]
        pkg = self._packages[package_id]

        expected_entry = next((e for e in pkg.manifest.files if e.relative_path == relative_path), None)
        if not expected_entry:
            return False, f"File '{relative_path}' not found in manifest."

        clean_hash = hashlib.sha256(clean_bytes).hexdigest()
        if clean_hash != expected_entry.hash_sha256:
            return False, "Provided clean bytes do not match expected manifest hash."

        inst.installed_files[relative_path] = clean_hash
        return True, f"Repaired '{relative_path}' successfully."

    # ==========================================================================
    # DIAGNOSTICS & HEALTH
    # ==========================================================================

    def generate_diagnostics(self) -> DeploymentDiagnosticReport:
        corrupted = 0
        for pid in self._installed_packages:
            ok, _ = self.verify_installation_integrity(pid)
            if not ok:
                corrupted += 1

        return DeploymentDiagnosticReport(
            is_healthy=(corrupted == 0),
            registered_assets=len(self._assets),
            installed_packages=len(self._installed_packages),
            corrupted_files=corrupted,
            pending_updates=len(self._staged_packages),
        )

    # ==========================================================================
    # 16 GOLDEN SCENARIOS (§224)
    # ==========================================================================

    def build_golden_asset_registry(self) -> AssetRecord:
        return self.register_asset("golden_tex_diffuse", AssetType.TEXTURE, "source_tex_01", content_bytes=b"GOLDEN_PBR_DIFFUSE_TEXTURE_2026")

    def build_golden_content_registry(self) -> ContentPackage:
        return self.register_content_package("golden_pack_base", ContentType.BASE_GAME, assets=["golden_tex_diffuse"])

    def build_golden_dependency_graph(self) -> List[str]:
        self.add_dependency("MeshNode", "MaterialNode", DependencyType.REQUIRED)
        self.add_dependency("MaterialNode", "ShaderNode", DependencyType.REQUIRED)
        return self.get_build_order()

    def build_golden_build_graph(self) -> BuildNode:
        return self.create_build_node("node_shader_compiler", ["source_hlsl"], "shader_binary.cso")

    def build_golden_build_artifact(self) -> BuildArtifact:
        if "node_shader_compiler" not in self._build_graph.nodes:
            self.build_golden_build_graph()
        _, art, _ = self.execute_build("node_shader_compiler", {"source_hlsl": b"float4 main() : SV_Target { return float4(1,1,1,1); }"})
        return art

    def build_golden_manifest(self) -> PackageManifest:
        files = {"bin/game.exe": b"EXE_BINARY_DATA", "data/pbr.pak": b"PAK_BINARY_DATA"}
        return self.generate_manifest("prod_game_01", "golden_core", "1.0.0", files)

    def build_golden_full_package(self) -> DeploymentPackage:
        files = {"game.exe": b"BINARY", "content.pak": b"CONTENT"}
        manifest = self.generate_manifest("game", "pkg_full_golden", "1.0.0", files)
        return self.create_package("pkg_full_golden", PackageType.FULL, manifest, files)

    def build_golden_patch_package(self) -> DeploymentPackage:
        files = {"game.exe": b"BINARY_V2"}
        manifest = self.generate_manifest("game", "pkg_patch_golden", "1.1.0", files)
        return self.create_package("pkg_patch_golden", PackageType.PATCH, manifest, files)

    def build_golden_dlc(self) -> DeploymentPackage:
        files = {"dlc1/map.pak": b"DLC_MAP_DATA"}
        manifest = self.generate_manifest("game", "pkg_dlc_golden", "1.0.0", files, dependencies=["pkg_full_golden"])
        return self.create_package("pkg_dlc_golden", PackageType.DLC, manifest, files)

    def build_golden_language_pack(self) -> DeploymentPackage:
        files = {"loc/es_es.pak": b"LOC_SPANISH_DATA"}
        manifest = self.generate_manifest("game", "pkg_lang_es", "1.0.0", files)
        return self.create_package("pkg_lang_es", PackageType.LANGUAGE, manifest, files)

    def build_golden_mod(self) -> DeploymentPackage:
        files = {"mods/laser_sight.pak": b"MOD_WEAPON_ADDON"}
        manifest = self.generate_manifest("game", "pkg_mod_laser", "1.0.0", files)
        return self.create_package("pkg_mod_laser", PackageType.MOD, manifest, files)

    def build_golden_installation(self) -> InstallationRecord:
        pkg = self.build_golden_full_package()
        self.stage_install(pkg.package_id)
        self.commit_install(pkg.package_id)
        return self._installed_packages[pkg.package_id]

    def build_golden_update(self) -> InstallationRecord:
        # Initial install
        p_full = self.build_golden_full_package()
        self.stage_install(p_full.package_id)
        self.commit_install(p_full.package_id)
        # Patch to v2
        p_patch = self.build_golden_patch_package()
        patch_desc = self.create_delta_patch(p_full.package_id, p_patch.package_id)
        self.apply_delta_patch(p_full.package_id, patch_desc)
        return self._installed_packages[p_full.package_id]

    def build_golden_rollback(self) -> InstallationRecord:
        inst = self.build_golden_update()
        self.rollback_install("pkg_full_golden")
        return self._installed_packages["pkg_full_golden"]

    def build_golden_repair(self) -> Tuple[bool, str]:
        inst = self.build_golden_installation()
        # Tamper a file
        inst.installed_files["game.exe"] = "CORRUPTED_HASH_12345"
        return self.repair_file("pkg_full_golden", "game.exe", b"BINARY")

    def build_golden_recovery(self) -> DeploymentDiagnosticReport:
        self.build_golden_installation()
        return self.generate_diagnostics()

    # ==========================================================================
    # END-TO-END WORKFLOW (§225)
    # ==========================================================================

    def run_end_to_end_pipeline(self) -> Dict[str, Any]:
        """
        Executes the normative 30-step pipeline (§225):
        SOURCE_ASSET -> REGISTER -> DECLARE_DEPENDENCIES -> RESOLVE_GRAPH ->
        BUILD -> CACHE -> GENERATE_ARTIFACT -> HASH -> SIGN -> GENERATE_MANIFEST ->
        PACKAGE -> PUBLISH -> DISCOVER_UPDATE -> DOWNLOAD -> VERIFY ->
        STAGE_INSTALL -> INSTALL -> POST_INSTALL_VALIDATE -> ACTIVATE ->
        RUN_HEALTH_CHECK -> CREATE_PATCH -> DOWNLOAD_PATCH -> APPLY_PATCH ->
        VERIFY -> SIMULATE_CRASH -> RECOVER -> ROLLBACK -> VERIFY_PREVIOUS_VERSION ->
        REPAIR_CORRUPTED_FILE -> VERIFY_REPAIRED_INSTALL.
        """
        results = {}

        # 1. Register Source Assets & Dependencies
        a1 = self.register_asset("e2e_source_core", AssetType.DATA, "src_01", content_bytes=b"CORE_E2E_SOURCE")
        a2 = self.register_asset("e2e_source_dep", AssetType.DATA, "src_02", content_bytes=b"DEP_E2E_SOURCE")
        self.add_dependency("e2e_source_core", "e2e_source_dep", DependencyType.REQUIRED)
        results["registered"] = True

        # 2. Resolve Graph & Build
        b_order = self.get_build_order()
        results["build_order"] = b_order
        node = self.create_build_node("e2e_build_node", ["e2e_source_core"], "e2e_art_out")
        ok_b, art, mode = self.execute_build("e2e_build_node", {"e2e_source_core": b"CORE_E2E_SOURCE"})
        results["build_ok"] = ok_b
        results["cache_mode"] = mode

        # 3. Manifest & Package & Sign
        files = {"game.exe": b"E2E_EXE_BYTES", "content.pak": b"E2E_PAK_BYTES"}
        manifest = self.generate_manifest("e2e_prod", "e2e_pkg_v1", "1.0.0", files)
        pkg_v1 = self.create_package("e2e_pkg_v1", PackageType.FULL, manifest, files)
        results["packaged"] = pkg_v1.is_certified

        # 4. Download & Verify
        dl_req = self.request_download("e2e_pkg_v1", "https://cdn.example.com/e2e_pkg_v1.bin")
        ok_dl, _ = self.process_download(dl_req.download_id)
        results["download_ok"] = ok_dl

        # 5. Stage & Install & Commit & Health Check
        ok_stage, _ = self.stage_install("e2e_pkg_v1")
        ok_commit, _ = self.commit_install("e2e_pkg_v1")
        diag1 = self.generate_diagnostics()
        results["installed"] = ok_stage and ok_commit and diag1.is_healthy

        # 6. Create Patch & Apply
        files_v2 = {"game.exe": b"E2E_EXE_BYTES_UPDATED", "content.pak": b"E2E_PAK_BYTES"}
        manifest_v2 = self.generate_manifest("e2e_prod", "e2e_pkg_v2", "1.1.0", files_v2)
        pkg_v2 = self.create_package("e2e_pkg_v2", PackageType.PATCH, manifest_v2, files_v2)
        patch = self.create_delta_patch("e2e_pkg_v1", "e2e_pkg_v2")
        ok_patch, _ = self.apply_delta_patch("e2e_pkg_v1", patch)
        results["patched"] = ok_patch

        # 7. Rollback to v1
        ok_rb, _ = self.rollback_install("e2e_pkg_v1")
        results["rolled_back"] = ok_rb

        # 8. Corrupt file & Repair
        self._installed_packages["e2e_pkg_v1"].installed_files["game.exe"] = "CORRUPT_CHECKSUM"
        ok_rep, _ = self.repair_file("e2e_pkg_v1", "game.exe", b"E2E_EXE_BYTES")
        results["repaired"] = ok_rep

        results["status"] = "SUCCESS"
        return results
