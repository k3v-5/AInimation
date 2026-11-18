"""
Universal Asset Processing Validation Pipeline.
Complies with UAF-81.71 specification.
"""

from typing import List, Tuple

from uaf.universal_processing.models.definition import (
    DerivedResource,
    LODChain,
    BuildManifest,
    ProcessingStateSnapshot,
    ProcessingDiagnosticBundle,
)


class UniversalProcessingValidator:
    """Normative validation suite for all derived resources, LODs, manifests and bundles."""

    @staticmethod
    def validate_derived_resource(resource: DerivedResource) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not resource.derived_resource_id or not resource.derived_resource_id.strip():
            errors.append("EMPTY_DERIVED_RESOURCE_ID: Derived resource ID cannot be empty.")
        if not resource.source_asset_id or not resource.source_asset_id.strip():
            errors.append("EMPTY_SOURCE_ASSET_ID: Source asset ID cannot be empty.")
        if not resource.processor_id or not resource.processor_id.strip():
            errors.append("EMPTY_PROCESSOR_ID: Processor ID cannot be empty.")
        if not resource.output_hash or len(resource.output_hash) != 64:
            errors.append(f"INVALID_OUTPUT_HASH: Output hash '{resource.output_hash}' must be a 64-character hex string.")
        if not resource.fingerprint or len(resource.fingerprint) != 64:
            errors.append(f"INVALID_FINGERPRINT: Fingerprint '{resource.fingerprint}' must be a 64-character hex string.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_lod_chain(chain: LODChain) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not chain.chain_id:
            errors.append("EMPTY_CHAIN_ID: LOD chain ID cannot be empty.")
        if not chain.levels:
            errors.append("EMPTY_LOD_CHAIN: Chain must contain at least one level.")
            return False, errors

        prev_tri = float("inf")
        prev_ratio = float("inf")
        for idx, lvl in enumerate(chain.levels):
            if lvl.level != idx:
                errors.append(f"LOD_SEQUENCE_DISORDER: Expected level {idx}, got {lvl.level}.")
            if lvl.triangle_count > prev_tri:
                errors.append(f"NON_MONOTONIC_LOD: LOD{lvl.level} triangle count ({lvl.triangle_count}) exceeds previous ({prev_tri}).")
            if lvl.triangle_ratio > prev_ratio:
                errors.append(f"NON_MONOTONIC_RATIO: LOD{lvl.level} ratio ({lvl.triangle_ratio}) exceeds previous ({prev_ratio}).")
            prev_tri = lvl.triangle_count
            prev_ratio = lvl.triangle_ratio

        return len(errors) == 0, errors

    @staticmethod
    def validate_build_manifest(manifest: BuildManifest) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not manifest.manifest_id or not manifest.manifest_id.strip():
            errors.append("EMPTY_MANIFEST_ID: Manifest ID cannot be empty.")
        expected_sig = manifest.compute_signature()
        if manifest.signature != expected_sig:
            errors.append(f"MANIFEST_SIGNATURE_MISMATCH: Expected '{expected_sig}', got '{manifest.signature}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_snapshot(snapshot: ProcessingStateSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not snapshot.snapshot_id or not snapshot.snapshot_id.strip():
            errors.append("EMPTY_SNAPSHOT_ID: Snapshot ID cannot be empty.")
        expected_h = snapshot.compute_state_hash()
        if snapshot.state_hash != expected_h:
            errors.append(f"SNAPSHOT_HASH_MISMATCH: Expected '{expected_h}', got '{snapshot.state_hash}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_diagnostic_bundle(bundle: ProcessingDiagnosticBundle) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not bundle.bundle_id or not bundle.bundle_id.strip():
            errors.append("EMPTY_BUNDLE_ID: Bundle ID cannot be empty.")
        expected_sig = bundle.compute_signature()
        if bundle.signature != expected_sig:
            errors.append(f"BUNDLE_SIGNATURE_MISMATCH: Expected '{expected_sig}', got '{bundle.signature}'.")
        ok_snap, snap_errs = UniversalProcessingValidator.validate_snapshot(bundle.snapshot)
        if not ok_snap:
            errors.extend(snap_errs)
        return len(errors) == 0, errors
