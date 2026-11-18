"""
UAF-81.35 Acceptance Tests (Sections 133, 127, 6, 10, 137, 138).
Verifies:
- Section 133: Final Acceptance Criteria (Generates and validates all 6 Golden Worlds:
  Room, Corridor, Building, Facility, Combat Area, City Block).
- Section 127: Hard Fail Conditions Test (Zero tolerance for isolated rooms, invalid spawns,
  invalid scale, invalid cell size, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.building_assembly.engine.building_assembly_fabricator import BuildingAssemblyFabricationPlatform
from uaf.building_assembly.validation.building_assembly_validator import BuildingAssemblyValidator
from uaf.building_assembly.models.definition import (
    BuildingAssemblySpecification,
    WorldType35,
    RoomType35,
    RoomDefinition35,
)
from uaf.building_assembly.package.building_assembly_package import BuildingAssemblyPackage


def test_final_building_assembly_acceptance_section_133():
    """
    Acceptance Test Section 133:
    Synthesizes and validates all 6 Golden Worlds.
    """
    builders = [
        ("World_Gold_Room", BuildingAssemblyFabricationPlatform.build_golden_room),
        ("World_Gold_Corridor", BuildingAssemblyFabricationPlatform.build_golden_corridor),
        ("World_Gold_Building", BuildingAssemblyFabricationPlatform.build_golden_building),
        ("World_Gold_Facility", BuildingAssemblyFabricationPlatform.build_golden_facility),
        ("World_Gold_CombatArea", BuildingAssemblyFabricationPlatform.build_golden_combat_area),
        ("World_Gold_CityBlock", BuildingAssemblyFabricationPlatform.build_golden_city_block),
    ]

    for world_id, builder_fn in builders:
        spec, level_path = builder_fn(world_id)
        assert spec.is_valid_grid is True

        report = BuildingAssemblyValidator.validate_building_assembly(spec, level_path)
        assert report.is_valid is True, f"Failed for {world_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = BuildingAssemblyPackage(
            world_id=world_id,
            spec=spec,
            level_asset_path=level_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["world_id"] == world_id


def test_hard_fail_conditions_section_127():
    """
    Acceptance Test Section 127:
    Hard fail conditions:
    1. ISOLATED_REQUIRED_ROOM: Room with no connections when total rooms > 1.
    2. INVALID_SPAWN: spawn_points_count < 1.
    3. INVALID_SCALE: Room dimensions invalid or ceiling height < 240.0 cm.
    4. INVALID_CELL_SIZE: Grid cell size < 50.0 cm.
    5. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, level_path = BuildingAssemblyFabricationPlatform.build_golden_building("World_Fault_Test")

    # 1. ISOLATED_REQUIRED_ROOM violation: Room added with zero connections
    iso_room = RoomDefinition35("Isolated_Bunker", RoomType35.STORAGE, [400.0, 400.0, 300.0], connected_room_ids=[])
    spec_iso = BuildingAssemblySpecification(
        "World_Iso",
        WorldType35.URBAN,
        rooms=spec.rooms + [iso_room],
    )
    rep_iso = BuildingAssemblyValidator.validate_building_assembly(spec_iso, level_path)
    assert rep_iso.is_valid is False
    assert rep_iso.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("ISOLATED_REQUIRED_ROOM" in iss for iss in rep_iso.issues)

    # 2. INVALID_SPAWN violation: 0 spawns
    spec_spawn = BuildingAssemblySpecification(
        "World_NoSpawn",
        WorldType35.URBAN,
        rooms=spec.rooms,
        spawn_points_count=0,
    )
    rep_spawn = BuildingAssemblyValidator.validate_building_assembly(spec_spawn, level_path)
    assert rep_spawn.is_valid is False
    assert rep_spawn.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_SPAWN" in iss for iss in rep_spawn.issues)

    # 3. INVALID_SCALE violation: Low ceiling height 180.0 cm (< 240.0 cm)
    low_room = RoomDefinition35("Low_Ceiling", RoomType35.OFFICE, [400.0, 400.0, 180.0], connected_room_ids=["Other"])
    spec_scale = BuildingAssemblySpecification(
        "World_LowCeiling",
        WorldType35.URBAN,
        rooms=[low_room],
    )
    rep_scale = BuildingAssemblyValidator.validate_building_assembly(spec_scale, level_path)
    assert rep_scale.is_valid is False
    assert rep_scale.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_SCALE" in iss for iss in rep_scale.issues)

    # 4. INVALID_CELL_SIZE violation: 25.0 cm (< 50.0 cm)
    spec_cell = BuildingAssemblySpecification(
        "World_TinyCell",
        WorldType35.URBAN,
        cell_size_cm=25.0,
        rooms=spec.rooms,
    )
    rep_cell = BuildingAssemblyValidator.validate_building_assembly(spec_cell, level_path)
    assert rep_cell.is_valid is False
    assert rep_cell.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_CELL_SIZE" in iss for iss in rep_cell.issues)

    # 5. Path purity violation: Absolute machine path
    bad_level_path = "D:\\UnrealProjects\\Maps\\Level_Test.umap"
    rep_path = BuildingAssemblyValidator.validate_building_assembly(spec, bad_level_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
