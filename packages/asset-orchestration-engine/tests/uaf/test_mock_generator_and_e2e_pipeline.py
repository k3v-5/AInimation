"""
UAF-81.0 Foundation Acceptance Test & End-to-End Pipeline Verification.
Tests the canonical flow:
Specification -> ExecutionContext -> Operation -> MockGenerator -> Artifact -> ContractValidator -> ArtifactManifest -> Publish
Completely self-contained, deterministic, and runnable without Blender or Unreal.
UAF-81.0 Sections 46, 54, 55, 56, 63.
"""

import tempfile
import pytest
from pathlib import Path

# Dual namespace imports verification
import uaf
import universal_asset_factory
from uaf import (
    ProjectContext,
    ExecutionContext,
    AssetIdentity,
    AssetType,
    AssetSpecification,
    ContractValidator,
    Artifact,
    ArtifactManifest,
    MockGenerator,
    OperationStatus,
)


def test_dual_namespace_imports():
    """Verify that both uaf and universal_asset_factory namespaces expose identical Foundation APIs."""
    assert uaf.AssetSpecification is universal_asset_factory.AssetSpecification
    assert uaf.ProjectContext is universal_asset_factory.ProjectContext
    assert uaf.MockGenerator is universal_asset_factory.MockGenerator
    assert uaf.CanonicalHasher is universal_asset_factory.CanonicalHasher


def test_mock_generator_determinism():
    """Verify that executing MockGenerator with the exact same seed produces bit-identical artifacts and hashes."""
    with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
        ctx1 = ProjectContext(project_id="run1", project_root=Path(tmp1))
        ctx1.ensure_directories()
        e_ctx1 = ExecutionContext(
            production_id="p1",
            operation_id="op1",
            asset_id="asset_hero_sword",
            project_context=ctx1,
            seed=4242,
        )

        ctx2 = ProjectContext(project_id="run2", project_root=Path(tmp2))
        ctx2.ensure_directories()
        e_ctx2 = ExecutionContext(
            production_id="p2",
            operation_id="op2",
            asset_id="asset_hero_sword",
            project_context=ctx2,
            seed=4242,
        )

        spec = AssetSpecification(
            identity=AssetIdentity(asset_id="asset_hero_sword", asset_type=AssetType.WEAPON),
            seed=4242,
            parameters={"damage": 100, "element": "fire"},
        )

        generator = MockGenerator()
        res1 = generator.execute(spec, e_ctx1)
        res2 = generator.execute(spec, e_ctx2)

        assert res1.is_success
        assert res2.is_success

        art1 = Artifact.from_dict(res1.artifacts[0])
        art2 = Artifact.from_dict(res2.artifacts[0])

        # Hashes and sizes must be identical
        assert art1.content_hash == art2.content_hash
        assert art1.size == art2.size
        assert art1.verify_integrity() is True
        assert art2.verify_integrity() is True


def test_mock_generator_different_seed_produces_different_hash():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = ProjectContext(project_id="run_diff", project_root=Path(tmp))
        ctx.ensure_directories()

        e_ctx1 = ExecutionContext(
            production_id="p1",
            operation_id="op1",
            asset_id="asset_diff",
            project_context=ctx,
            seed=100,
        )
        e_ctx2 = ExecutionContext(
            production_id="p2",
            operation_id="op2",
            asset_id="asset_diff",
            project_context=ctx,
            seed=200,
        )

        spec1 = AssetSpecification(
            identity=AssetIdentity(asset_id="asset_diff", asset_type=AssetType.PROP),
            seed=100,
        )
        spec2 = AssetSpecification(
            identity=AssetIdentity(asset_id="asset_diff", asset_type=AssetType.PROP),
            seed=200,
        )

        generator = MockGenerator()
        res1 = generator.execute(spec1, e_ctx1)
        res2 = generator.execute(spec2, e_ctx2)

        art1 = Artifact.from_dict(res1.artifacts[0])
        art2 = Artifact.from_dict(res2.artifacts[0])

        assert art1.content_hash != art2.content_hash


def test_full_uaf_foundation_end_to_end_acceptance_pipeline():
    """
    Executes the entire UAF-81.0 Foundation end-to-end acceptance flow:
    1. Create ProjectContext (isolated, drive-agnostic)
    2. Create AssetSpecification (immutable, validated)
    3. Validate Specification via ContractValidator
    4. Create ExecutionContext (immutable execution environment)
    5. Execute MockGenerator
    6. Retrieve produced Artifact and verify cryptographic integrity
    7. Validate Artifact via ContractValidator
    8. Build ArtifactManifest linking Asset, Operations, Artifacts, and Provenance
    9. Validate Manifest
    10. Publish Manifest to project output directory
    """
    with tempfile.TemporaryDirectory() as sandbox_dir:
        # Step 1: Create ProjectContext
        project_root = Path(sandbox_dir) / "E2E_Test_Project"
        project_context = ProjectContext(project_id="uaf_e2e_acceptance", project_root=project_root)
        project_context.ensure_directories()

        # Step 2: Create AssetSpecification
        identity = AssetIdentity(
            asset_id="sci_fi_tactical_helmet",
            asset_type=AssetType.ARMOR if hasattr(AssetType, "ARMOR") else AssetType.PROP,
            namespace="gear",
            version="1.0.0",
        )
        spec = AssetSpecification(
            identity=identity,
            target="unreal_engine_5.5",
            quality_profile="production",
            parameters={
                "color_scheme": "matte_carbon",
                "visor_tint": "gold_reflective",
                "night_vision_enabled": True,
            },
            seed=81081,
        )

        # Step 3: Validate Specification
        spec_report = ContractValidator.validate_specification(spec)
        assert spec_report.is_valid is True, f"Specification validation failed: {spec_report.diagnostics}"

        # Step 4: Create ExecutionContext
        exec_context = ExecutionContext(
            production_id="prod_e2e_001",
            operation_id="op_generate_helmet_mesh",
            asset_id=spec.identity.asset_id,
            project_context=project_context,
            seed=spec.seed,
            target=spec.target,
            quality_profile=spec.quality_profile,
        )

        # Step 5: Execute MockGenerator
        generator = MockGenerator()
        op_result = generator.execute(spec, exec_context)

        assert op_result.status == OperationStatus.SUCCEEDED
        assert len(op_result.artifacts) == 1

        # Step 6: Retrieve produced Artifact and verify cryptographic integrity
        artifact = Artifact.from_dict(op_result.artifacts[0])
        assert artifact.verify_integrity() is True
        assert artifact.size > 0
        assert len(artifact.content_hash) == 64

        # Step 7: Validate Artifact via ContractValidator
        artifact_report = ContractValidator.validate_artifact(artifact)
        assert artifact_report.is_valid is True

        # Step 8: Build ArtifactManifest
        manifest = ArtifactManifest(
            manifest_id=f"manifest_{spec.identity.asset_id}",
            asset_id=spec.identity.asset_id,
            production_id=exec_context.production_id,
            artifacts=[artifact],
            operations=[exec_context.operation_id],
            metadata={"specification_hash": spec.specification_hash},
        )

        # Step 9: Validate Manifest
        manifest_report = ContractValidator.validate_manifest(manifest, verify_artifacts=True)
        assert manifest_report.is_valid is True

        # Step 10: Publish Manifest to output root
        output_manifest_path = project_context.output_root / f"{manifest.manifest_id}.json"
        import json
        with open(output_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2)

        assert output_manifest_path.exists()
        assert output_manifest_path.stat().st_size > 0

        # Reload published manifest and verify
        with open(output_manifest_path, "r", encoding="utf-8") as f:
            published_data = json.load(f)
        reloaded_manifest = ArtifactManifest.from_dict(published_data)

        assert reloaded_manifest.asset_id == "sci_fi_tactical_helmet"
        assert len(reloaded_manifest.artifacts) == 1
        assert reloaded_manifest.artifacts[0].verify_integrity() is True
