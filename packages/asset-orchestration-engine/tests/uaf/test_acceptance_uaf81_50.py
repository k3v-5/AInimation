"""
UAF-81.50 Acceptance Tests (Sections 149, 148, 157, 158, 161, 153, 156).
Verifies:
- Section 149: Final Acceptance Criteria (Generates and validates all 5 Golden Environments:
  Interior, Facility, Urban Block, Industrial, Dungeon).
- Sections 148, 157, 158, 161: Hard Fail Conditions Test (Zero tolerance for invalid assembly dimensions,
  height < 3m, grid snap < 10cm, zero modules, missing collision, nav, lighting, or world partition, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.modular_assembly_system.engine.modular_assembly_fabricator import ModularAssemblyFabricationPlatform
from uaf.modular_assembly_system.validation.modular_assembly_validator import ModularAssemblyValidator
from uaf.modular_assembly_system.models.definition import (
    ModularAssemblySpecification,
    EnvironmentType50,
    AssemblyDimensions50,
)
from uaf.modular_assembly_system.package.modular_assembly_package import ModularAssemblyPackage


def test_final_modular_assembly_acceptance_section_149():
    """
    Acceptance Test Section 149:
    Synthesizes and validates all 5 Golden Environments.
    """
    builders = [
        ("Env_Gold_Interior50", ModularAssemblyFabricationPlatform.build_golden_interior),
        ("Env_Gold_Facility50", ModularAssemblyFabricationPlatform.build_golden_facility),
        ("Env_Gold_UrbanBlock50", ModularAssemblyFabricationPlatform.build_golden_urban_block),
        ("Env_Gold_Industrial50", ModularAssemblyFabricationPlatform.build_golden_industrial),
        ("Env_Gold_Dungeon50", ModularAssemblyFabricationPlatform.build_golden_dungeon),
    ]

    for env_id, builder_fn in builders:
        spec, lvl_path, part_path, nav_path = builder_fn(env_id)
        assert spec.is_valid_assembly is True

        report = ModularAssemblyValidator.validate_modular_assembly(spec, lvl_path, part_path, nav_path)
        assert report.is_valid is True, f"Failed for {env_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = ModularAssemblyPackage(
            environment_id=env_id,
            spec=spec,
            level_asset_path=lvl_path,
            world_partition_path=part_path,
            navmesh_path=nav_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["environment_id"] == env_id


def test_hard_fail_conditions_section_148_157_158_161():
    """
    Acceptance Test Sections 148, 157, 158, 161:
    Hard fail conditions:
    1. INVALID_ASSEMBLY_DIMENSIONS: Height < 3m or non-positive spans.
    2. INVALID_GRID_OR_MODULES: Grid snap < 10cm or module count < 1.
    3. MISSING_CORE_SUBSYSTEMS: Missing collision, navigation, lighting, or world partition.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, lvl_path, part_path, nav_path = ModularAssemblyFabricationPlatform.build_golden_interior("Env_Fault_Test")

    # 1. Height clearance violation: 2.0m (< 3.0m)
    bad_dims = AssemblyDimensions50(width_m=30.0, length_m=30.0, height_m=2.0)
    bad_spec_dims = ModularAssemblySpecification(
        "Env_LowCeiling",
        EnvironmentType50.INTERIOR,
        dimensions=bad_dims,
    )
    rep_dims = ModularAssemblyValidator.validate_modular_assembly(bad_spec_dims, lvl_path, part_path, nav_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_ASSEMBLY_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Grid snap violation: 5cm (< 10cm)
    bad_spec_grid = ModularAssemblySpecification(
        "Env_TinySnap",
        EnvironmentType50.INTERIOR,
        grid_snap_cm=5.0,
    )
    rep_grid = ModularAssemblyValidator.validate_modular_assembly(bad_spec_grid, lvl_path, part_path, nav_path)
    assert rep_grid.is_valid is False
    assert rep_grid.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_GRID_OR_MODULES" in iss for iss in rep_grid.issues)

    # 3. Missing lighting setup
    bad_spec_light = ModularAssemblySpecification(
        "Env_NoLight",
        EnvironmentType50.INTERIOR,
        has_lighting=False,
    )
    rep_light = ModularAssemblyValidator.validate_modular_assembly(bad_spec_light, lvl_path, part_path, nav_path)
    assert rep_light.is_valid is False
    assert rep_light.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_light.issues)

    # 4. Path purity violation: Absolute machine path
    bad_lvl_path = "D:\\UnrealProjects\\Levels\\L_Interior.umap"
    rep_path = ModularAssemblyValidator.validate_modular_assembly(spec, bad_lvl_path, part_path, nav_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
