"""
Tests for Modular Assembly Models, Dimensions, and Grid Snapping.
UAF-81.50 Sections 4, 5, 8, 12, 149, 151.
"""

from uaf.modular_assembly_system.models.definition import (
    EnvironmentType50,
    ModularPieceType50,
    AssemblyDimensions50,
    ModularAssemblySpecification,
)


def test_assembly_dimensions_and_validity():
    dims_ok = AssemblyDimensions50(width_m=40.0, length_m=40.0, height_m=6.0)
    assert dims_ok.is_valid is True

    dims_low = AssemblyDimensions50(width_m=40.0, length_m=40.0, height_m=1.8)  # < 3.0m clearance
    assert dims_low.is_valid is False

    dims_neg = AssemblyDimensions50(width_m=-10.0, length_m=20.0, height_m=5.0)
    assert dims_neg.is_valid is False


def test_modular_assembly_specification_and_hashing():
    spec = ModularAssemblySpecification(
        environment_id="Env_Test_Assembly",
        environment_type=EnvironmentType50.FACILITY,
        dimensions=AssemblyDimensions50(width_m=60.0, length_m=60.0, height_m=10.0),
        grid_snap_cm=50.0,
        module_count=48,
        has_collision=True,
        has_navigation=True,
        has_lighting=True,
        has_world_partition=True,
        seed=654321,
    )

    assert spec.is_valid_assembly is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["environment_type"] == "FACILITY"
    assert data["module_count"] == 48

    bad_spec_snap = ModularAssemblySpecification(
        environment_id="Env_BadSnap",
        environment_type=EnvironmentType50.FACILITY,
        grid_snap_cm=5.0,  # < 10.0cm
    )
    assert bad_spec_snap.is_valid_assembly is False
