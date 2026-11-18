"""
Tests for Modular World Fabrication Platform, Validation, and Package.
UAF-81.19 Sections 182, 209, 212, 213.
"""

from uaf.modular_world.engine.modular_world_fabricator import ModularWorldFabricationPlatform
from uaf.modular_world.validation.modular_world_validator import ModularWorldValidator
from uaf.modular_world.package.modular_world_package import ModularWorldPackage


def test_modular_world_fabrication_eight_canonical_archetypes():
    archetypes = [
        ModularWorldFabricationPlatform.build_room_environment,
        ModularWorldFabricationPlatform.build_building_environment,
        ModularWorldFabricationPlatform.build_facility_environment,
        ModularWorldFabricationPlatform.build_combat_arena_environment,
        ModularWorldFabricationPlatform.build_dungeon_environment,
        ModularWorldFabricationPlatform.build_scifi_complex_environment,
        ModularWorldFabricationPlatform.build_modular_district_environment,
        ModularWorldFabricationPlatform.build_world_cell_environment,
    ]

    for builder in archetypes:
        env_def, graph, modules, props = builder()
        assert len(graph.rooms) > 0
        assert graph.is_fully_connected() is True
        assert modules > 0
        assert props > 0


def test_modular_world_package_validation_and_serialization():
    env_def, graph, modules, props = ModularWorldFabricationPlatform.build_facility_environment("Env_ResearchBase")

    report = ModularWorldValidator.validate_environment(env_def, graph, modules, props)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = ModularWorldPackage(
        asset_id="Env_ResearchBase",
        environment_def=env_def,
        layout_graph=graph,
        modules_placed_count=modules,
        props_placed_count=props,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Env_ResearchBase"
    assert data["modules_placed_count"] == modules
    assert data["validation_report"]["review_status"] == "PASSED"
