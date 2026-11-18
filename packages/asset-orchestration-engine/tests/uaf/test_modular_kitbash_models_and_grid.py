"""
Tests for Modular Kitbash Models, Dimensions, and Grid Snapping.
UAF-81.39 Sections 5, 6, 7, 8, 10, 13, 16, 17, 136, 144.
"""

from uaf.modular_kitbash.models.definition import (
    ModuleType39,
    PivotType39,
    SnapMode39,
    KitStyle39,
    ModuleDimensions39,
    ModularKitbashSpecification,
)


def test_modular_kitbash_dimensions_and_validity():
    dims_ok = ModuleDimensions39(width_cm=200.0, depth_cm=20.0, height_cm=300.0)
    assert dims_ok.is_valid is True

    dims_neg = ModuleDimensions39(width_cm=0.0, depth_cm=20.0, height_cm=300.0)
    assert dims_neg.is_valid is False


def test_modular_kitbash_specification_and_hashing():
    spec = ModularKitbashSpecification(
        kitbash_id="Kitbash_Test_Wall",
        kit_style=KitStyle39.SCI_FI_KIT,
        root_type=ModuleType39.WALL,
        dimensions=ModuleDimensions39(width_cm=400.0, depth_cm=20.0, height_cm=300.0),
        pivot=PivotType39.BASE_CENTER,
        snap_mode=SnapMode39.GRID,
        grid_snap_size_cm=50.0,
        socket_count=4,
        module_count=2,
        seed=12345,
    )

    assert spec.is_valid_structure is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["kit_style"] == "SCI_FI_KIT"
    assert data["socket_count"] == 4

    bad_spec_snap = ModularKitbashSpecification(
        kitbash_id="Kitbash_BadSnap",
        kit_style=KitStyle39.SCI_FI_KIT,
        root_type=ModuleType39.WALL,
        grid_snap_size_cm=5.0,  # < 10.0 cm
    )
    assert bad_spec_snap.is_valid_structure is False

    bad_spec_soc = ModularKitbashSpecification(
        kitbash_id="Kitbash_ZeroSockets",
        kit_style=KitStyle39.SCI_FI_KIT,
        root_type=ModuleType39.WALL,
        socket_count=0,
    )
    assert bad_spec_soc.is_valid_structure is False
