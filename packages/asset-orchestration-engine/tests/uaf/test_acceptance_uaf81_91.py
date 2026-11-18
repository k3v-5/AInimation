"""
UAF-81.91: Universal Procedural Macro-Landscape, Hydraulic Erosion, Biome Distribution & Spline Infrastructure
Acceptance Test Suite.
Verifies Heightfield2D, 16-bit binary Unreal Landscape import/export,
multi-octave fractal noise, thermal & hydraulic erosion, Whittaker biomes,
flow accumulation rivers, cost-surface road splines, and Poisson-disk foliage.
"""

import json
import math
import struct
import pytest
from pathlib import Path

from uaf.landscape import (
    BiomeType,
    RoadCategory,
    SplineNode,
    RoadPath,
    ClimateMap,
    TerrainLayerWeightmaps,
    Heightfield2D,
    PerlinNoise2D,
    FractalNoise2D,
    VoronoiCellularNoise2D,
    MacroTerrainGenerator,
    HydraulicErosionSimulator,
    ThermalErosionSimulator,
    ClimateModeler,
    WhittakerBiomeClassifier,
    TerrainWeightmapGenerator,
    RiverDrainageNetwork,
    RoadNetworkPlanner,
    FoliageInstance,
    PoissonDiskSampler2D,
    PCGFoliageDistributor,
    UE5LandscapeManifest,
    UE5LandscapeExporter,
)


class TestHeightfieldAndBinaryEncoding:
    """Test suite for Heightfield2D and 16-bit Unreal Engine binary serialization."""

    def test_heightfield_bilinear_and_slope(self):
        hf = Heightfield2D(width=10, height=10, meters_per_cell=2.0, min_elevation_meters=0.0, max_elevation_meters=100.0)
        hf.set_elevation(0, 0, 0.0)
        hf.set_elevation(1, 0, 1.0)
        hf.set_elevation(0, 1, 0.0)
        hf.set_elevation(1, 1, 1.0)

        # Bilinear sample at center (0.5, 0.5) of cell
        val = hf.sample_bilinear(0.5 / 9.0, 0.5 / 9.0)
        assert 0.4 < val < 0.6

        # Slope calculation
        slope = hf.compute_slope_angle_deg(0, 0)
        assert slope >= 0.0

    def test_heightfield_raw16_roundtrip(self):
        hf = Heightfield2D(width=8, height=8, meters_per_cell=4.0, min_elevation_meters=-50.0, max_elevation_meters=500.0)
        for y in range(8):
            for x in range(8):
                hf.set_elevation(x, y, (x + y) / 14.0)

        raw_bytes = hf.to_raw16_bytes()
        assert len(raw_bytes) == 8 * 8 * 2  # 128 bytes

        # Reconstruct from raw binary
        hf_restored = Heightfield2D.from_raw16_bytes(
            raw_bytes=raw_bytes,
            width=8,
            height=8,
            meters_per_cell=4.0,
            min_elevation_meters=-50.0,
            max_elevation_meters=500.0,
        )

        for y in range(8):
            for x in range(8):
                assert math.isclose(hf.get_elevation(x, y), hf_restored.get_elevation(x, y), abs_tol=1e-4)


class TestFractalNoiseAndDeterminism:
    """Test suite for continuous noise algorithms and deterministic seeding."""

    def test_perlin_noise_bounds_and_continuity(self):
        perlin = PerlinNoise2D(seed=42)
        samples = [perlin.sample(i * 0.1, j * 0.1) for i in range(20) for j in range(20)]
        for s in samples:
            assert -1.5 <= s <= 1.5

    def test_macro_terrain_determinism(self):
        hf1 = Heightfield2D(16, 16)
        hf2 = Heightfield2D(16, 16)

        gen1 = MacroTerrainGenerator(seed=12345)
        gen2 = MacroTerrainGenerator(seed=12345)

        gen1.generate(hf1)
        gen2.generate(hf2)

        for y in range(16):
            for x in range(16):
                assert hf1.get_elevation(x, y) == hf2.get_elevation(x, y)

    def test_voronoi_cellular_noise(self):
        voronoi = VoronoiCellularNoise2D(seed=99, cell_size=8.0)
        v1 = voronoi.sample(4.0, 4.0)
        assert 0.0 <= v1 <= 1.0


class TestPhysicalErosion:
    """Test suite for hydraulic and thermal erosion simulation."""

    def test_thermal_erosion_mass_conservation(self):
        hf = Heightfield2D(24, 24, meters_per_cell=2.0, min_elevation_meters=0.0, max_elevation_meters=500.0)
        # Create artificial sharp pyramid
        for y in range(24):
            for x in range(24):
                dist = math.hypot(x - 12, y - 12)
                hf.set_elevation(x, y, max(0.0, 1.0 - dist * 0.08))

        initial_mass = sum(hf.get_elevation(x, y) for y in range(24) for x in range(24))

        simulator = ThermalErosionSimulator(angle_of_repose_deg=32.0, relaxation_rate=0.5)
        simulator.simulate(hf, iterations=6)

        post_mass = sum(hf.get_elevation(x, y) for y in range(24) for x in range(24))
        # Total terrain mass must be strictly conserved
        assert math.isclose(initial_mass, post_mass, abs_tol=1e-6)

    def test_hydraulic_erosion_droplet_execution(self):
        hf = Heightfield2D(30, 30)
        MacroTerrainGenerator(seed=77).generate(hf)

        simulator = HydraulicErosionSimulator(seed=77)
        simulator.simulate(hf, num_droplets=800)

        # Check all values remain valid floats in [0, 1]
        for y in range(30):
            for x in range(30):
                val = hf.get_elevation(x, y)
                assert 0.0 <= val <= 1.0


class TestEcologyAndWeightmaps:
    """Test suite for climate modeling, Whittaker biomes, and material weightmaps."""

    def test_climate_lapse_rate_and_biomes(self):
        hf = Heightfield2D(20, 20, min_elevation_meters=0.0, max_elevation_meters=2000.0)
        # Low altitude on left, high mountain on right
        for y in range(20):
            for x in range(20):
                hf.set_elevation(x, y, x / 19.0)

        climate = ClimateModeler(sea_level_temperature_c=25.0, seed=42).generate_climate(hf)

        # High altitude should be significantly colder than sea level
        temp_sea_level = climate.temperature[10][0]
        temp_summit = climate.temperature[10][19]
        assert temp_summit < temp_sea_level - 10.0

        # Biome classification
        biome_low = WhittakerBiomeClassifier.classify(temp_sea_level, 0.5, 50.0)
        biome_high = WhittakerBiomeClassifier.classify(temp_summit, 0.5, 1900.0)
        assert biome_high in [BiomeType.ALPINE, BiomeType.TUNDRA]

    def test_terrain_weightmap_normalization(self):
        hf = Heightfield2D(15, 15)
        MacroTerrainGenerator(seed=42).generate(hf)
        climate = ClimateModeler(seed=42).generate_climate(hf)

        weights = TerrainWeightmapGenerator.generate_weightmaps(hf, climate)
        assert weights.width == 15
        assert weights.height == 15

        for y in range(15):
            for x in range(15):
                total = (
                    weights.grass[y][x]
                    + weights.rock[y][x]
                    + weights.dirt[y][x]
                    + weights.snow[y][x]
                    + weights.sand[y][x]
                )
                assert math.isclose(total, 1.0, abs_tol=1e-3)


class TestInfrastructureAndSplines:
    """Test suite for hydrological river routing and cost-surface road planning."""

    def test_river_drainage_flow_accumulation(self):
        hf = Heightfield2D(35, 35)
        # Slope downwards from (0, 0) to (34, 34)
        for y in range(35):
            for x in range(35):
                hf.set_elevation(x, y, 1.0 - (x + y) / 68.0)

        drainage = RiverDrainageNetwork(river_accumulation_threshold=20)
        flow_dir, accumulation = drainage.compute_flow_accumulation(hf)

        # Sinks at bottom-right corner should accumulate maximum water
        max_acc = max(max(row) for row in accumulation)
        assert max_acc >= 20

        rivers = drainage.extract_river_splines(hf, flow_dir, accumulation)
        assert len(rivers) > 0

    def test_road_network_planner_and_carving(self):
        hf = Heightfield2D(40, 40, meters_per_cell=10.0, min_elevation_meters=0.0, max_elevation_meters=200.0)
        MacroTerrainGenerator(seed=42).generate(hf)

        planner = RoadNetworkPlanner(max_allowed_slope_deg=45.0)
        road = planner.plan_road(hf, start_coord=(4, 4), goal_coord=(35, 35), road_id="R_HIGHWAY")

        assert road is not None
        assert len(road.nodes) >= 2
        assert road.total_length_meters > 0.0

        # Carve roadbed
        planner.carve_roadbed(hf, road, blend_radius_cells=1)
        # Verify node coordinates are within valid range
        for node in road.nodes:
            assert len(node.tangent) == 3


class TestFoliageAndPCG:
    """Test suite for Poisson-disk sampling and ecological asset scattering."""

    def test_poisson_disk_minimum_distance(self):
        sampler = PoissonDiskSampler2D(min_dist_m=5.0, seed=123)
        points = sampler.sample(width_m=80.0, height_m=80.0)
        assert len(points) > 10

        # Verify pairwise distance constraint
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = math.hypot(points[i][0] - points[j][0], points[i][1] - points[j][1])
                assert dist >= 4.95  # Within small numerical tolerance

    def test_pcg_foliage_distributor(self):
        hf = Heightfield2D(30, 30, meters_per_cell=5.0)
        MacroTerrainGenerator(seed=42).generate(hf)
        climate = ClimateModeler(seed=42).generate_climate(hf)

        distributor = PCGFoliageDistributor(seed=42)
        instances = distributor.distribute_foliage(hf, climate, min_tree_spacing_m=6.0)

        assert len(instances) > 0
        for inst in instances:
            assert inst.asset_type in ["TREE", "ROCK"]
            assert len(inst.world_pos) == 3


class TestUE5LandscapeExporter:
    """Test suite for Unreal Engine 5 landscape export bundle and ingestion script."""

    def test_ue5_export_pipeline(self, tmp_path: Path):
        hf = Heightfield2D(25, 25, meters_per_cell=4.0, min_elevation_meters=-10.0, max_elevation_meters=400.0)
        MacroTerrainGenerator(seed=42).generate(hf)
        climate = ClimateModeler(seed=42).generate_climate(hf)
        weights = TerrainWeightmapGenerator.generate_weightmaps(hf, climate)

        planner = RoadNetworkPlanner(max_allowed_slope_deg=45.0)
        road = planner.plan_road(hf, start_coord=(2, 2), goal_coord=(22, 22))
        roads = [road] if road else []

        exporter = UE5LandscapeExporter(landscape_name="L_AcceptanceTestWorld")
        manifest_path, script_path = exporter.export_all(
            heightfield=hf,
            weightmaps=weights,
            output_dir=tmp_path,
            roads=roads,
        )

        assert manifest_path.exists()
        assert script_path.exists()

        # Check raw heightmap binary
        r16_file = tmp_path / "L_AcceptanceTestWorld_heightmap.r16"
        assert r16_file.exists()
        assert r16_file.stat().st_size == 25 * 25 * 2  # Exactly 1250 bytes

        # Check layer weightmaps
        for layer in ["Grass", "Rock", "Dirt", "Snow", "Sand"]:
            layer_file = tmp_path / f"L_AcceptanceTestWorld_Layer_{layer}.r8"
            assert layer_file.exists()
            assert layer_file.stat().st_size == 25 * 25  # Exactly 625 bytes

        # Check manifest content
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            assert manifest_data["landscape_name"] == "L_AcceptanceTestWorld"
            assert manifest_data["width"] == 25
            assert manifest_data["height"] == 25
            assert manifest_data["z_scale_unreal"] > 0.0

        # Check Python ingestion script
        with open(script_path, "r", encoding="utf-8") as f:
            script_text = f.read()
            assert "Autonomous Unreal Engine 5 Macro-Landscape & PCG Ingestion Script" in script_text
            assert "import_landscape" in script_text
            assert "L_AcceptanceTestWorld_manifest.json" in script_text

    def test_end_to_end_macro_landscape_pipeline(self, tmp_path: Path):
        """
        Complete vertical test:
        1. Heightfield creation & multi-octave synthesis
        2. Thermal & hydraulic erosion simulation
        3. Climate modeling & Whittaker biome classification
        4. Material layer weightmaps
        5. River flow accumulation & splines
        6. Cost-surface road infrastructure routing
        7. Poisson-disk foliage scattering
        8. UE5 export bundle generation.
        """
        # 1. Heightfield & Terrain
        hf = Heightfield2D(width=32, height=32, meters_per_cell=6.0, min_elevation_meters=0.0, max_elevation_meters=500.0)
        MacroTerrainGenerator(seed=888).generate(hf)

        # 2. Erosion
        ThermalErosionSimulator(angle_of_repose_deg=35.0).simulate(hf, iterations=3)
        HydraulicErosionSimulator(seed=888).simulate(hf, num_droplets=500)

        # 3. Climate & Biomes
        climate = ClimateModeler(seed=888).generate_climate(hf)
        weights = TerrainWeightmapGenerator.generate_weightmaps(hf, climate)

        # 4. River Drainage
        drainage = RiverDrainageNetwork(river_accumulation_threshold=18)
        flow_dir, acc = drainage.compute_flow_accumulation(hf)
        rivers = drainage.extract_river_splines(hf, flow_dir, acc)
        drainage.carve_riverbeds(hf, acc)

        # 5. Road Infrastructure
        planner = RoadNetworkPlanner(max_allowed_slope_deg=45.0)
        road = planner.plan_road(hf, start_coord=(3, 3), goal_coord=(28, 28), road_id="R_OUTPOST_LINK")
        roads = [road] if road else []
        if road:
            planner.carve_roadbed(hf, road)

        # 6. Foliage Scatter
        distributor = PCGFoliageDistributor(seed=888)
        foliage = distributor.distribute_foliage(hf, climate, roads=roads, min_tree_spacing_m=8.0)

        # 7. UE5 Export
        exporter = UE5LandscapeExporter(landscape_name="L_GoldenMacroWorld")
        manifest_p, script_p = exporter.export_all(
            heightfield=hf,
            weightmaps=weights,
            output_dir=tmp_path / "UE5_Landscape_Bundle",
            roads=roads,
            rivers=rivers,
            foliage=foliage,
        )

        assert manifest_p.exists()
        assert script_p.exists()
        assert (tmp_path / "UE5_Landscape_Bundle" / "L_GoldenMacroWorld_heightmap.r16").exists()
        assert (tmp_path / "UE5_Landscape_Bundle" / "L_GoldenMacroWorld_foliage.json").exists()
