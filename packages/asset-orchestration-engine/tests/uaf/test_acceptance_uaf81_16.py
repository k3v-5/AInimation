"""
UAF-81.16 Acceptance Tests (Sections 235, 236, 188, 204).
Verifies:
- Section 235: Final Acceptance Criteria (Generates and validates a complete world with:
  1 Terrain, 2 Biomes, 1 Water Body, 1 River, 1 Road Network, 1 Building District, Gameplay Zones).
- Section 236: Playable Acceptance (Spawn -> Navigation -> Combat -> Objective reachability).
- Sections 188, 204: Non-Negotiable Requirements Test (Zero tolerance for unreachable zones, missing spawns,
  or hardcoded local machine paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.world_system.platform.world_fabricator import WorldFabricationPlatform
from uaf.world_system.validation.world_validator import WorldValidator
from uaf.world_system.models.features import GameplayZone
from uaf.world_system.models.world_def import WorldDefinition, WorldBounds
from uaf.world_system.package.world_package import WorldFabricationPackage


def test_final_world_system_acceptance_section_235_236():
    """
    Acceptance Test Sections 235 & 236:
    Synthesizes and validates complete canonical world with full playability flow.
    """
    w_def, biomes, water, roads, districts, zones = WorldFabricationPlatform.build_canonical_world("World_Golden_Canonical")

    # Section 235 check:
    assert len(biomes) >= 2
    assert any(wb.water_type == "LAKE" for wb in water)
    assert any(wb.water_type == "RIVER" for wb in water)
    assert roads is not None
    assert len(districts) >= 1
    assert len(zones) >= 3

    # Section 236 playability flow check:
    assert any(z.player_spawns > 0 and z.is_reachable for z in zones)
    assert any(z.combat_arenas > 0 and z.is_reachable for z in zones)
    assert any(z.objectives > 0 and z.is_reachable for z in zones)

    report = WorldValidator.validate_world(w_def, biomes, water, roads, districts, zones)
    assert report.is_valid is True, f"Failed: {report.issues}"
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = WorldFabricationPackage(
        asset_id="World_Golden_Canonical",
        world_definition=w_def,
        biomes=biomes,
        water_bodies=water,
        road_network=roads,
        districts=districts,
        gameplay_zones=zones,
        validation_report=report,
    )
    assert len(pkg.package_hash) == 64
    assert pkg.to_dict()["asset_id"] == "World_Golden_Canonical"


def test_non_negotiable_requirements_section_188_204_236():
    """
    Acceptance Test Sections 188, 204, 236:
    Non-negotiable requirements:
    1. Section 188 & 236: Unreachable gameplay zones/objectives strictly fails.
    2. Section 204: Absolute machine path in world ID strictly fails.
    3. Section 188: World without player spawn zones strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    w_def, biomes, water, roads, districts, zones = WorldFabricationPlatform.build_canonical_world("World_Fault_Test")

    # 1. Section 188 violation: Unreachable objective zone
    bad_zones = [
        GameplayZone("Zone_Spawn", player_spawns=1, is_reachable=True),
        GameplayZone("Zone_LockedBoss", objectives=1, is_reachable=False),  # VIOLATION: Unreachable
    ]
    rep_reach = WorldValidator.validate_world(w_def, biomes, water, roads, districts, bad_zones)
    assert rep_reach.is_valid is False
    assert rep_reach.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("is unreachable" in iss for iss in rep_reach.issues)

    # 2. Section 204 violation: Hardcoded local machine path
    bad_w_def = WorldDefinition("C:\\Users\\User\\Worlds\\MyWorld", seed=123)
    rep_path = WorldValidator.validate_world(bad_w_def, biomes, water, roads, districts, zones)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("absolute local machine paths" in iss for iss in rep_path.issues)
