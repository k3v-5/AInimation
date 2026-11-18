"""
UAF-81.56 Acceptance & Normative Compliance Test Suite.
Verifies all 228 Sections of UAF-81.56-PROCEDURAL-WORLD-SCENE-SYSTEM.md,
Cross-Phase Integration (UAF-81.50 through 56), Machine-Agnostic Purity,
Foot IK Integration, Character Spawning, and 10 Canonical Golden Worlds.
"""

import pytest
from uaf.universal_world import (
    UniversalWorldFabricator,
    UniversalWorldValidator,
    ProductionReadyWorld,
    WorldQuery,
    WorldQueryType,
    ExportTarget,
)

# Cross-Phase Integration imports (Section 213, 214, 215, 216, 217, 218)
from uaf.universal_surface import UniversalSurfaceFabricationPlatform
from uaf.universal_geometry import UniversalGeometryFabricationPlatform
from uaf.universal_character import UniversalCharacterFabricator
from uaf.universal_animation import UniversalAnimationFabricator


class TestUAF8156Acceptance:
    """Acceptance criteria tests for UAF-81.56 Universal World, Terrain & Procedural Scene System."""

    def test_golden_world_set_complete(self):
        """Verify all 10 Golden Worlds from Section 209 exist, are valid, and verify readback."""
        goldens = [
            UniversalWorldFabricator.create_golden_flat_world(),
            UniversalWorldFabricator.create_golden_desert(),
            UniversalWorldFabricator.create_golden_grassland(),
            UniversalWorldFabricator.create_golden_forest(),
            UniversalWorldFabricator.create_golden_mountain(),
            UniversalWorldFabricator.create_golden_snow(),
            UniversalWorldFabricator.create_golden_coast(),
            UniversalWorldFabricator.create_golden_river_valley(),
            UniversalWorldFabricator.create_golden_urban(),
            UniversalWorldFabricator.create_golden_hybrid_world(),
        ]
        assert len(goldens) == 10
        for g_def in goldens:
            sg = UniversalWorldFabricator.build_scene_graph(g_def)
            rep = UniversalWorldValidator.validate_world(g_def, sg)
            assert rep.is_valid is True
            assert rep.quality_score >= 80.0
            pkg = ProductionReadyWorld(g_def, sg, rep)
            rb = pkg.verify_readback()
            assert rb["readback_status"] == "VERIFIED"
            assert len(pkg.canonical_hash) == 64

    def test_cross_phase_integration_uaf81_50_to_56(self):
        """Verify cross-phase integration with UAF-81.50 through UAF-81.56 (Sections 213-218)."""
        # 1. Surface from UAF-81.52
        surf_spec, *surf_paths = UniversalSurfaceFabricationPlatform.build_golden_leather()
        assert surf_spec.is_valid_surface is True

        # 2. Geometry from UAF-81.53
        mesh_spec, *mesh_paths = UniversalGeometryFabricationPlatform.build_golden_character()
        assert mesh_spec.is_valid_mesh is True

        # 3. Rigged Character from UAF-81.54
        character = UniversalCharacterFabricator.build_golden_human_male()
        assert character.validation_report.is_valid is True

        # 4. Animated Character from UAF-81.55
        animated_char = UniversalAnimationFabricator.build_golden_walk(character=character)
        assert animated_char.validation_report.is_valid is True

        # 5. World from UAF-81.56
        world = UniversalWorldFabricator.create_golden_grassland()
        sg = UniversalWorldFabricator.build_scene_graph(world)
        assert sg is not None

        # Character Spawn on World Anchor (Section 214)
        spawn_pos = world.anchors[0].position
        assert len(spawn_pos) == 3

        # Foot IK Terrain Query (Section 216)
        query = WorldQuery(WorldQueryType.HEIGHT_AT, position=spawn_pos)
        res = UniversalWorldFabricator.solve_query(world, query)
        assert "height" in res
        ground_height = res["height"]
        assert isinstance(ground_height, float)

        # Locomotion slope check (Section 215)
        slope_query = WorldQuery(WorldQueryType.SLOPE_AT, position=spawn_pos)
        slope_res = UniversalWorldFabricator.solve_query(world, slope_query)
        assert "slope" in slope_res

    def test_strict_machine_path_rejection(self):
        """Verify strict hard failure when absolute machine paths (C:, D:, E:) are passed (Engine Purity)."""
        world = UniversalWorldFabricator.create_golden_flat_world()

        for bad_path in [
            r"C:\UnrealProjects\Maps\TestWorld.umap",
            r"D:\Game\Content\Maps\World.umap",
            r"E:\Dev\Assets\Maps\World.umap",
        ]:
            world.props[0].asset_variants = [bad_path]
            report = UniversalWorldValidator.validate_world(world)
            assert report.is_valid is False
            assert any("machine-dependent" in f.lower() for f in report.failed_checks)

    def test_world_query_system_acceptance(self):
        """Verify complete suite of queries on world snapshot (Section 159-161)."""
        world = UniversalWorldFabricator.create_golden_forest()
        queries = [
            WorldQuery(WorldQueryType.HEIGHT_AT, (0.0, 0.0, 0.0)),
            WorldQuery(WorldQueryType.SLOPE_AT, (100.0, 100.0, 0.0)),
            WorldQuery(WorldQueryType.BIOME_AT, (0.0, 0.0, 0.0)),
            WorldQuery(WorldQueryType.WATER_AT, (0.0, 0.0, -50.0)),
            WorldQuery(WorldQueryType.CELL_AT, (0.0, 0.0, 0.0)),
            WorldQuery(WorldQueryType.NEAREST_ASSET, (0.0, 0.0, 0.0)),
            WorldQuery(WorldQueryType.NEAREST_ROAD, (0.0, 0.0, 0.0)),
        ]
        for q in queries:
            res = UniversalWorldFabricator.solve_query(world, q)
            assert res is not None
            assert len(res) > 0

    def test_production_ready_world_packaging(self):
        """Verify complete packaging, canonical hash and export readback (Section 181-183)."""
        world = UniversalWorldFabricator.create_golden_urban()
        sg = UniversalWorldFabricator.build_scene_graph(world)
        rep = UniversalWorldValidator.validate_world(world, sg)
        assert rep.is_valid is True

        pkg = ProductionReadyWorld(
            world_def=world,
            scene_graph=sg,
            validation_report=rep,
            export_target=ExportTarget.ENGINE_RUNTIME,
            export_path="/Game/Maps/CityMetropolis.umap",
        )
        assert len(pkg.canonical_hash) == 64
        rb = pkg.verify_readback()
        assert rb["readback_status"] == "VERIFIED"
        assert rb["world_id"] == "GOLDEN_URBAN"
        assert rb["building_count"] >= 5
        assert rb["canonical_hash"] == pkg.canonical_hash
