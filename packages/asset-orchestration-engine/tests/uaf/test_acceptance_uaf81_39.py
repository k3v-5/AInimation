"""
UAF-81.39 Acceptance Tests (Sections 136, 141, 7, 8, 10, 23, 140, 146).
Verifies:
- Section 136: Final Acceptance Criteria (Generates and validates all 6 Golden Assemblies:
  Corridor, Room, Building, Industrial Facility, Sci-Fi Facility, Modular Kit).
- Section 141: Hard Fail Conditions Test (Zero tolerance for invalid dimensions, zero sockets,
  invalid grid snap sizes, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.modular_kitbash.engine.modular_kitbash_fabricator import ModularKitbashFabricationPlatform
from uaf.modular_kitbash.validation.modular_kitbash_validator import ModularKitbashValidator
from uaf.modular_kitbash.models.definition import (
    ModularKitbashSpecification,
    KitStyle39,
    ModuleType39,
    ModuleDimensions39,
)
from uaf.modular_kitbash.package.modular_kitbash_package import ModularKitbashPackage


def test_final_modular_kitbash_acceptance_section_136():
    """
    Acceptance Test Section 136:
    Synthesizes and validates all 6 Golden Assemblies.
    """
    builders = [
        ("Kitbash_Gold_Corridor", ModularKitbashFabricationPlatform.build_golden_corridor),
        ("Kitbash_Gold_Room", ModularKitbashFabricationPlatform.build_golden_room),
        ("Kitbash_Gold_Building", ModularKitbashFabricationPlatform.build_golden_building),
        ("Kitbash_Gold_IndFacility", ModularKitbashFabricationPlatform.build_golden_industrial_facility),
        ("Kitbash_Gold_SciFiFacility", ModularKitbashFabricationPlatform.build_golden_sci_fi_facility),
        ("Kitbash_Gold_ModularKit", ModularKitbashFabricationPlatform.build_golden_modular_kit),
    ]

    for kit_id, builder_fn in builders:
        spec, sm_path, bp_path = builder_fn(kit_id)
        assert spec.is_valid_structure is True

        report = ModularKitbashValidator.validate_modular_kitbash(spec, sm_path, bp_path)
        assert report.is_valid is True, f"Failed for {kit_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = ModularKitbashPackage(
            kitbash_id=kit_id,
            spec=spec,
            static_mesh_path=sm_path,
            blueprint_path=bp_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["kitbash_id"] == kit_id


def test_hard_fail_conditions_section_141():
    """
    Acceptance Test Section 141:
    Hard fail conditions:
    1. INVALID_DIMENSIONS: Non-positive width, depth, or height.
    2. ZERO_SOCKETS: socket_count < 1.
    3. INVALID_GRID_SNAP: grid_snap_size_cm < 10.0 cm.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, sm_path, bp_path = ModularKitbashFabricationPlatform.build_golden_corridor("Kitbash_Fault_Test")

    # 1. Dimension violation: width_cm = -20.0
    bad_dims = ModuleDimensions39(width_cm=-20.0, depth_cm=200.0, height_cm=300.0)
    bad_spec_dims = ModularKitbashSpecification(
        "Kitbash_BadDims",
        KitStyle39.SCI_FI_KIT,
        ModuleType39.WALL,
        dimensions=bad_dims,
    )
    rep_dims = ModularKitbashValidator.validate_modular_kitbash(bad_spec_dims, sm_path, bp_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Socket count violation: 0 sockets
    bad_spec_soc = ModularKitbashSpecification(
        "Kitbash_NoSockets",
        KitStyle39.SCI_FI_KIT,
        ModuleType39.WALL,
        socket_count=0,
    )
    rep_soc = ModularKitbashValidator.validate_modular_kitbash(bad_spec_soc, sm_path, bp_path)
    assert rep_soc.is_valid is False
    assert rep_soc.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("ZERO_SOCKETS" in iss for iss in rep_soc.issues)

    # 3. Grid snap violation: 5cm (< 10cm)
    bad_spec_snap = ModularKitbashSpecification(
        "Kitbash_BadSnap",
        KitStyle39.SCI_FI_KIT,
        ModuleType39.WALL,
        grid_snap_size_cm=5.0,
    )
    rep_snap = ModularKitbashValidator.validate_modular_kitbash(bad_spec_snap, sm_path, bp_path)
    assert rep_snap.is_valid is False
    assert rep_snap.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_GRID_SNAP" in iss for iss in rep_snap.issues)

    # 4. Path purity violation: Absolute machine path
    bad_sm_path = "D:\\UnrealProjects\\Modular\\SM_Corridor.uasset"
    rep_path = ModularKitbashValidator.validate_modular_kitbash(spec, bad_sm_path, bp_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
