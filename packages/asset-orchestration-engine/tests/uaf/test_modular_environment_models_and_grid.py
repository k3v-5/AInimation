"""
Tests for Modular Environment Models, Dimensions, and Grid Snapping.
UAF-81.47 Sections 4, 5, 6, 8, 12, 131, 170.
"""

from uaf.modular_environment.models.definition import (
    ModuleCategory47,
    SnapType47,
    EnvironmentStyle47,
    EnvironmentDimensions47,
    ModularEnvironmentSpecification,
)


def test_environment_dimensions_and_validity():
    dims_ok = EnvironmentDimensions47(width_m=25.0, length_m=30.0, height_m=4.0)
    assert dims_ok.is_valid is True

    dims_neg = EnvironmentDimensions47(width_m=-10.0, length_m=20.0, height_m=4.0)
    assert dims_neg.is_valid is False

    dims_low_height = EnvironmentDimensions47(width_m=20.0, length_m=20.0, height_m=2.0)  # < 3.0m
    assert dims_low_height.is_valid is False


def test_modular_environment_specification_and_hashing():
    spec = ModularEnvironmentSpecification(
        environment_id="Env_Test_Hangar",
        style=EnvironmentStyle47.MILITARY,
        category=ModuleCategory47.STRUCTURAL,
        dimensions=EnvironmentDimensions47(width_m=40.0, length_m=50.0, height_m=10.0),
        grid_snap_cm=100.0,
        module_count=32,
        has_collision=True,
        has_navigation=True,
        has_gameplay_anchors=True,
        seed=654321,
    )

    assert spec.is_valid_environment is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["style"] == "MILITARY"
    assert data["module_count"] == 32

    bad_spec_modules = ModularEnvironmentSpecification(
        environment_id="Env_ZeroModules",
        style=EnvironmentStyle47.MILITARY,
        module_count=0,  # < 1
    )
    assert bad_spec_modules.is_valid_environment is False
