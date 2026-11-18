"""
UAF-81.47 Acceptance Tests (Sections 131, 144, 156, 157, 158, 160, 161, 162, 163, 164, 165, 151, 167).
Verifies:
- Section 131: Final Acceptance Criteria (Generates and validates all 6 Golden Environments:
  Room, Corridor, Building, Facility, Indoor Map, Outdoor Map).
- Sections 144, 156, 157, 158, 161, 162, 163, 164, 165: Hard Fail Conditions Test (Zero tolerance for invalid dimensions,
  height < 3m, grid snap < 10cm, zero modules, missing collision/nav/gameplay anchors, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.modular_environment.engine.modular_environment_fabricator import ModularEnvironmentFabricationPlatform
from uaf.modular_environment.validation.modular_environment_validator import ModularEnvironmentValidator
from uaf.modular_environment.models.definition import (
    ModularEnvironmentSpecification,
    EnvironmentStyle47,
    EnvironmentDimensions47,
)
from uaf.modular_environment.package.modular_environment_package import ModularEnvironmentPackage


def test_final_modular_environment_acceptance_section_131():
    """
    Acceptance Test Section 131:
    Synthesizes and validates all 6 Golden Environments.
    """
    builders = [
        ("Env_Gold_Room", ModularEnvironmentFabricationPlatform.build_golden_room),
        ("Env_Gold_Corridor", ModularEnvironmentFabricationPlatform.build_golden_corridor),
        ("Env_Gold_Building", ModularEnvironmentFabricationPlatform.build_golden_building),
        ("Env_Gold_Facility", ModularEnvironmentFabricationPlatform.build_golden_facility),
        ("Env_Gold_IndoorMap", ModularEnvironmentFabricationPlatform.build_golden_indoor_map),
        ("Env_Gold_OutdoorMap", ModularEnvironmentFabricationPlatform.build_golden_outdoor_map),
    ]

    for env_id, builder_fn in builders:
        spec, level_path, nav_path, col_path = builder_fn(env_id)
        assert spec.is_valid_environment is True

        report = ModularEnvironmentValidator.validate_modular_environment(spec, level_path, nav_path, col_path)
        assert report.is_valid is True, f"Failed for {env_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = ModularEnvironmentPackage(
            environment_id=env_id,
            spec=spec,
            level_asset_path=level_path,
            navmesh_path=nav_path,
            collision_asset_path=col_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["environment_id"] == env_id


def test_hard_fail_conditions_section_144_156_157_158_161_162_163_164_165():
    """
    Acceptance Test Sections 144, 156, 157, 158, 161, 162, 163, 164, 165:
    Hard fail conditions:
    1. INVALID_DIMENSIONS: Non-positive width/length or height < 3m.
    2. INVALID_GRID_OR_MODULES: grid_snap_cm < 10.0cm or module_count < 1.
    3. MISSING_CORE_SUBSYSTEMS: has_collision, has_navigation, or has_gameplay_anchors is False.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, level_path, nav_path, col_path = ModularEnvironmentFabricationPlatform.build_golden_room("Env_Fault_Test")

    # 1. Height violation: 1.5m (< 3.0m clearance)
    bad_dims = EnvironmentDimensions47(width_m=10.0, length_m=10.0, height_m=1.5)
    bad_spec_dims = ModularEnvironmentSpecification(
        "Env_LowHeight",
        EnvironmentStyle47.SCI_FI,
        dimensions=bad_dims,
    )
    rep_dims = ModularEnvironmentValidator.validate_modular_environment(bad_spec_dims, level_path, nav_path, col_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Grid snap violation: 5cm (< 10cm)
    bad_spec_grid = ModularEnvironmentSpecification(
        "Env_TinyGrid",
        EnvironmentStyle47.SCI_FI,
        grid_snap_cm=5.0,
    )
    rep_grid = ModularEnvironmentValidator.validate_modular_environment(bad_spec_grid, level_path, nav_path, col_path)
    assert rep_grid.is_valid is False
    assert rep_grid.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_GRID_OR_MODULES" in iss for iss in rep_grid.issues)

    # 3. Missing gameplay anchors
    bad_spec_anchors = ModularEnvironmentSpecification(
        "Env_NoAnchors",
        EnvironmentStyle47.SCI_FI,
        has_gameplay_anchors=False,
    )
    rep_anchors = ModularEnvironmentValidator.validate_modular_environment(bad_spec_anchors, level_path, nav_path, col_path)
    assert rep_anchors.is_valid is False
    assert rep_anchors.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_anchors.issues)

    # 4. Path purity violation: Absolute machine path
    bad_lvl_path = "D:\\UnrealProjects\\Environments\\L_Room.umap"
    rep_path = ModularEnvironmentValidator.validate_modular_environment(spec, bad_lvl_path, nav_path, col_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
