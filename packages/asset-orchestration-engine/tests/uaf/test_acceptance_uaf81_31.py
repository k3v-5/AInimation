"""
UAF-81.31 Acceptance Tests (Sections 129, 144, 7, 12, 16, 125).
Verifies:
- Sections 129, 144: Final Acceptance Criteria (Generates and validates all 4 canonical reference kits:
  Sci-Fi Corridor Kit, Industrial Room Kit, Urban Building Kit, Bunker Kit).
- Sections 7, 12, 16, 125: Non-Negotiable Requirements Test (Zero tolerance for invalid grid scaling,
  invalid piece dimensions, missing sockets, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.modular_architecture.engine.architecture_fabricator import ModularArchitectureFabricationPlatform
from uaf.modular_architecture.validation.architecture_validator import ModularArchitectureValidator
from uaf.modular_architecture.models.definition import (
    ModularArchitectureKitDefinition,
    ArchitecturalKitType31,
    ModuleType31,
    SocketType31,
    ArchitecturalModulePiece,
)
from uaf.modular_architecture.package.architecture_package import ModularArchitecturePackage


def test_final_modular_architecture_acceptance_sections_129_and_144():
    """
    Acceptance Test Sections 129 and 144:
    Synthesizes and validates all 4 canonical reference kits.
    """
    builders = [
        ("Kit_Gold_SciFi", ModularArchitectureFabricationPlatform.build_scifi_corridor_kit),
        ("Kit_Gold_Industrial", ModularArchitectureFabricationPlatform.build_industrial_room_kit),
        ("Kit_Gold_Urban", ModularArchitectureFabricationPlatform.build_urban_building_kit),
        ("Kit_Gold_Bunker", ModularArchitectureFabricationPlatform.build_bunker_kit),
    ]

    for asset_id, builder_fn in builders:
        kit_def, mesh_refs, mat_ref = builder_fn(asset_id)
        assert kit_def.is_valid_grid is True
        assert len(kit_def.pieces) >= 4

        report = ModularArchitectureValidator.validate_architecture_kit(kit_def, mesh_refs, mat_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = ModularArchitecturePackage(
            asset_id=asset_id,
            kit_def=kit_def,
            static_mesh_refs=mesh_refs,
            master_material_ref=mat_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_7_12_16_125():
    """
    Acceptance Test Sections 7, 12, 16, 125:
    Non-negotiable requirements:
    1. Section 7 & 125: Grid unit < 100cm strictly fails.
    2. Section 125: Non-positive piece dimensions strictly fails.
    3. Section 16 & 125: Missing sockets strictly fails.
    4. Section 125: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    kit_def, mesh_refs, mat_ref = ModularArchitectureFabricationPlatform.build_scifi_corridor_kit("Kit_Fault_Test")

    # 1. Section 7 & 125 violation: Grid unit < 100cm
    bad_kit_grid = ModularArchitectureKitDefinition(
        "Kit_BadGrid",
        ArchitecturalKitType31.SCI_FI_CORRIDOR_KIT,
        grid_unit_cm=50.0,
        pieces=kit_def.pieces,
    )
    rep_grid = ModularArchitectureValidator.validate_architecture_kit(bad_kit_grid, mesh_refs, mat_ref)
    assert rep_grid.is_valid is False
    assert rep_grid.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("below the 100.0cm threshold" in iss for iss in rep_grid.issues)

    # 2. Section 125 violation: Piece with non-positive dimensions
    bad_piece = ArchitecturalModulePiece("Wall_BadDim", ModuleType31.WALL, [400.0, -10.0, 300.0], [SocketType31.WALL_START])
    bad_kit_dim = ModularArchitectureKitDefinition(
        "Kit_BadDim",
        ArchitecturalKitType31.SCI_FI_CORRIDOR_KIT,
        grid_unit_cm=400.0,
        pieces=[bad_piece],
    )
    rep_dim = ModularArchitectureValidator.validate_architecture_kit(bad_kit_dim, ["SM_Wall_BadDim"], mat_ref)
    assert rep_dim.is_valid is False
    assert rep_dim.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("invalid or non-positive dimensions" in iss for iss in rep_dim.issues)

    # 3. Section 16 & 125 violation: Piece with zero sockets
    piece_no_sockets = ArchitecturalModulePiece("Wall_NoSockets", ModuleType31.WALL, [400.0, 30.0, 300.0], sockets=[])
    bad_kit_sock = ModularArchitectureKitDefinition(
        "Kit_NoSockets",
        ArchitecturalKitType31.SCI_FI_CORRIDOR_KIT,
        grid_unit_cm=400.0,
        pieces=[piece_no_sockets],
    )
    rep_sock = ModularArchitectureValidator.validate_architecture_kit(bad_kit_sock, ["SM_Wall_NoSockets"], mat_ref)
    assert rep_sock.is_valid is False
    assert rep_sock.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("zero snapping sockets" in iss for iss in rep_sock.issues)

    # 4. Section 125 violation: Absolute machine path in material reference
    bad_mat_path = "E:\\UnrealProjects\\Kit\\M_Master_PBR.uasset"
    rep_path = ModularArchitectureValidator.validate_architecture_kit(kit_def, mesh_refs, bad_mat_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
