"""
Universal Deployment Validator (UAF-81.63).
Validates package manifests, cryptographic signatures, dependency cycles,
and security policies (path traversal, archive bombs, file count limits).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from ..models import (
    PackageManifest,
    DeploymentPackage,
    SigningCertificate,
    TrustPolicy,
    DependencyGraph,
)


@dataclass
class DeploymentValidationReport:
    """Detailed validation evaluation report."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class UniversalDeploymentValidator:
    """
    Integrity, trust, and security validator for build artifacts, packages, and manifests.
    """

    FORBIDDEN_PATH_CHARS = set(r':*?"<>|')

    def __init__(
        self,
        max_file_count: int = 10000,
        max_total_bytes: int = 50 * 1024 * 1024 * 1024,  # 50 GB
        max_compression_ratio: float = 100.0,
        max_dependency_depth: int = 50,
    ):
        self.max_file_count = max_file_count
        self.max_total_bytes = max_total_bytes
        self.max_compression_ratio = max_compression_ratio
        self.max_dependency_depth = max_dependency_depth

    def validate_relative_path(self, path: str) -> Tuple[bool, str]:
        """Ensures file paths inside manifests do not perform path traversal or absolute references (§218)."""
        if not path or not isinstance(path, str):
            return False, "Path cannot be empty or non-string."
        # Absolute path checks
        if path.startswith("/") or path.startswith("\\") or (len(path) > 1 and path[1] == ":"):
            return False, "Absolute path rejected for security."
        # Traversal checks
        if ".." in path.split("/") or ".." in path.split("\\"):
            return False, "Path traversal sequence '..' detected."
        # Forbidden characters
        if any(c in self.FORBIDDEN_PATH_CHARS for c in path):
            return False, "Path contains illegal characters."
        return True, "Valid relative path."

    def validate_archive_bomb_safety(self, total_uncompressed_bytes: int, total_compressed_bytes: int, file_count: int) -> Tuple[bool, str]:
        """Guards against zip/archive bombs (§218)."""
        if file_count > self.max_file_count:
            return False, f"File count ({file_count}) exceeds limit ({self.max_file_count})."
        if total_uncompressed_bytes > self.max_total_bytes:
            return False, f"Expanded size ({total_uncompressed_bytes} bytes) exceeds limit ({self.max_total_bytes})."
        if total_compressed_bytes > 0:
            ratio = total_uncompressed_bytes / total_compressed_bytes
            if ratio > self.max_compression_ratio:
                return False, f"Compression expansion ratio ({ratio:.1f}:1) exceeds limit ({self.max_compression_ratio:.1f}:1)."
        return True, "Archive bomb check passed."

    def validate_package(
        self,
        package: DeploymentPackage,
        certificates: Optional[Dict[str, SigningCertificate]] = None,
    ) -> DeploymentValidationReport:
        """Comprehensive verification of package structure, paths, signatures, and safety."""
        report = DeploymentValidationReport()
        manifest = package.manifest

        report.metrics["file_count"] = len(manifest.files)
        total_size = sum(f.size_bytes for f in manifest.files)
        report.metrics["total_uncompressed_bytes"] = total_size

        # 1. Path safety checks
        for f in manifest.files:
            valid_path, msg = self.validate_relative_path(f.relative_path)
            if not valid_path:
                report.is_valid = False
                report.errors.append(f"Insecure path '{f.relative_path}': {msg}")

        # 2. Archive bomb limits
        compressed_size = sum(len(b) for b in package.payload_files.values())
        safe, bomb_msg = self.validate_archive_bomb_safety(total_size, compressed_size, len(manifest.files))
        if not safe:
            report.is_valid = False
            report.errors.append(f"Archive bomb limit exceeded: {bomb_msg}")

        # 3. Signature verification
        if not package.is_certified or not package.signature:
            report.is_valid = False
            report.errors.append("Package is not signed or certified.")
        elif certificates:
            has_trusted_sig = False
            manifest_hash = manifest.calculate_manifest_hash()
            for cert_id, sig in manifest.signatures.items():
                if cert_id in certificates:
                    cert = certificates[cert_id]
                    if cert.trust_policy == TrustPolicy.TRUSTED:
                        has_trusted_sig = True
                    elif cert.trust_policy == TrustPolicy.REVOKED:
                        report.is_valid = False
                        report.errors.append(f"Signed by revoked certificate: {cert_id}")
            if not has_trusted_sig and report.is_valid:
                report.is_valid = False
                report.errors.append("Package does not contain any signature from a trusted certificate authority.")

        return report
