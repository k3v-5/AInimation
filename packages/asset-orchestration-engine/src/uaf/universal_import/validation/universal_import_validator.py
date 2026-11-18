"""
UAF-81.70: Universal Asset Import Pipeline Validator.
Enforces normative invariants for Source Identities, Graph Acyclicity,
Import Profiles, Job Integrity, Manifest Signatures, and Cryptographic Telemetry.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from uaf.universal_import.models.definition import (
    FormatDescriptor,
    ImportDiagnosticBundle,
    ImportJob,
    ImportManifest,
    ImportProfile,
    ImportStateSnapshot,
    ProcessingGraph,
    SourceIdentity,
    normalize_source_path,
)


class UniversalImportValidator:
    """
    Authoritative validator enforcing normative invariants for the Universal Asset Import Pipeline.
    """

    @staticmethod
    def validate_source_path(path_str: str) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not path_str or not isinstance(path_str, str):
            errors.append("EMPTY_PATH: Source path must be a non-empty string.")
            return False, errors

        if ".." in path_str:
            errors.append(f"NO_NON_CANONICAL_SOURCE_PATH: Path traversal '..' in '{path_str}'.")
        if "\\" in path_str:
            errors.append(f"NO_NON_CANONICAL_SOURCE_PATH: Backslash in '{path_str}'.")
        if "//" in path_str:
            errors.append(f"NO_NON_CANONICAL_SOURCE_PATH: Consecutive slashes in '{path_str}'.")
        if re.search(r'[<>:"|?*]', path_str):
            errors.append(f"INVALID_CHARS: Source path '{path_str}' contains forbidden characters.")

        try:
            normalize_source_path(path_str)
        except Exception as e:
            errors.append(f"NORMALIZATION_ERROR: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_source_identity(source: SourceIdentity) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not source.source_id:
            errors.append("EMPTY_SOURCE_ID: Source ID must not be empty.")

        path_ok, path_errs = UniversalImportValidator.validate_source_path(source.canonical_path)
        if not path_ok:
            errors.extend(path_errs)

        if len(source.content_hash) != 64:
            errors.append(f"INVALID_HASH: Content hash '{source.content_hash}' must be 64 hex characters.")

        if source.file_size_bytes < 0:
            errors.append("NEGATIVE_SIZE: Source file size cannot be negative.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_format_descriptor(format_desc: FormatDescriptor) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not format_desc.format_id:
            errors.append("EMPTY_FORMAT_ID: Format ID must not be empty.")
        if not format_desc.name:
            errors.append("EMPTY_FORMAT_NAME: Format name must not be empty.")
        for ext in format_desc.extensions:
            if not ext.startswith("."):
                errors.append(f"INVALID_EXTENSION: Extension '{ext}' must start with a dot.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_import_profile(profile: ImportProfile) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not profile.profile_id:
            errors.append("EMPTY_PROFILE_ID: Profile ID must not be empty.")
        if not profile.target_format:
            errors.append("EMPTY_TARGET_FORMAT: Target format must not be empty.")
        if not profile.processor_id:
            errors.append("EMPTY_PROCESSOR_ID: Processor ID must not be empty.")
        if profile.parent_profile_id == profile.profile_id:
            errors.append(f"NO_GRAPH_CYCLES: Profile '{profile.profile_id}' cannot be its own parent.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_processing_graph(graph: ProcessingGraph) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not graph.graph_id:
            errors.append("EMPTY_GRAPH_ID: Graph ID must not be empty.")

        if graph.detect_cycles():
            errors.append(f"NO_GRAPH_CYCLES: Graph '{graph.graph_id}' contains cycles.")

        for edge in graph.edges:
            if edge.source_node_id not in graph.nodes:
                errors.append(f"MISSING_SOURCE_NODE: Source node '{edge.source_node_id}' does not exist.")
            if edge.target_node_id not in graph.nodes:
                errors.append(f"MISSING_TARGET_NODE: Target node '{edge.target_node_id}' does not exist.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_import_job(job: ImportJob) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not job.job_id:
            errors.append("EMPTY_JOB_ID: Job ID must not be empty.")
        if not job.source_id:
            errors.append("EMPTY_SOURCE_ID: Job source ID must not be empty.")
        if not job.profile_id:
            errors.append("EMPTY_PROFILE_ID: Job profile ID must not be empty.")
        if not (0.0 <= job.progress <= 1.0):
            errors.append(f"INVALID_PROGRESS: Job progress {job.progress} must be in [0.0, 1.0].")
        if job.retry_count < 0 or job.retry_count > job.max_retries:
            errors.append(f"INVALID_RETRY_COUNT: Retry count {job.retry_count} exceeds bounds.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_manifest(manifest: ImportManifest) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected_sig = manifest.compute_signature()
        if manifest.signature != expected_sig:
            errors.append(f"MANIFEST_CORRUPTION: Expected signature '{expected_sig}', got '{manifest.signature}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_snapshot(snapshot: ImportStateSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected_hash = snapshot.compute_hash()
        if snapshot.state_hash != expected_hash:
            errors.append(f"SNAPSHOT_CORRUPTION: Expected hash '{expected_hash}', got '{snapshot.state_hash}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_diagnostic_bundle(bundle: ImportDiagnosticBundle) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected_sig = bundle.sign()
        if bundle.signature != expected_sig:
            errors.append(f"BUNDLE_CORRUPTION: Expected signature '{expected_sig}', got '{bundle.signature}'.")
        return len(errors) == 0, errors
