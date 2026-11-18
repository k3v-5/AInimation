"""
Acceptance Test Suite for UAF-81.102:
One-Click Full Vertical Slice Builder (Macro-Orchestrator).

Validates end-to-end procedural synergy across:
1. Macro-Landscape & Ecology
2. Spatial Constraint Solver & Bunker Pad Flattening
3. WFC Modular Sci-Fi Bunker Interior
4. Tactical AI Squads & StateTree Integration
5. Volumetric Weather & Diurnal Sky Atmosphere
6. Chaos Voronoi Fracture & Geometry Collections
7. Interactive MetaSounds & Room Acoustics
8. Autonomous QA Headless Playtest Certification
9. Master Package Integrator, UE5 Automation Script & CLI
"""

import os
import sys
import shutil
import tempfile
import subprocess
import zipfile
import pytest

from uaf.macro_orchestrator.core.contracts import (
    VerticalSliceConfig,
    SliceSize,
    OrchestrationStage,
    SpatialFootprint,
    IntegratedSliceManifest,
)
from uaf.macro_orchestrator.spatial.constraint_solver import SpatialConstraintSolver
from uaf.macro_orchestrator.orchestrator.slice_orchestrator import VerticalSliceMasterOrchestrator
from uaf.macro_orchestrator.integrator.package_integrator import (
    MasterPackageIntegrator,
    PackageResult,
)
from uaf.macro_orchestrator.cli.slice_cli import (
    build_vertical_slice,
    create_cli_parser,
    run_cli,
)
from uaf.weather_atmosphere import WeatherBiomeType
from uaf.landscape.core import Heightfield2D


class TestUAF81102MacroOrchestrator:

    @pytest.fixture
    def temp_out_dir(self):
        d = tempfile.mkdtemp(prefix="uaf102_test_")
        yield d
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)

    def test_01_config_defaults_and_validation(self):
        cfg = VerticalSliceConfig(slice_name="Test_Alpha")
        assert cfg.slice_name == "Test_Alpha"
        assert cfg.size == SliceSize.MEDIUM
        assert cfg.biome == WeatherBiomeType.TEMPERATE_FOREST
        assert cfg.seed == 42
        assert cfg.enable_chaos_destruction is True
        assert cfg.enable_metasounds_audio is True
        assert cfg.enable_ai_patrols is True

    def test_02_spatial_constraint_solver_plateau_finding(self):
        hf = Heightfield2D(
            width=64,
            height=64,
            meters_per_cell=4.0,
            min_elevation_meters=0.0,
            max_elevation_meters=350.0,
            initial_elevation=0.3,
        )
        solver = SpatialConstraintSolver()
        footprint = solver.solve_placement(hf, wfc_dimensions=(4, 4), tile_size_meters=6.0)

        assert footprint.footprint_cells_x > 0
        assert footprint.footprint_cells_y > 0
        assert 0 <= footprint.center_world_cm[0] <= 25600.0
        assert 0 <= footprint.center_world_cm[1] <= 25600.0
        assert footprint.pad_elevation_m > 0
        assert footprint.safety_buffer_cm >= 30.0

    def test_03_spatial_constraint_solver_pad_flattening(self):
        hf = Heightfield2D(
            width=64,
            height=64,
            meters_per_cell=4.0,
            min_elevation_meters=0.0,
            max_elevation_meters=350.0,
            initial_elevation=0.3,
        )
        # Give slope
        for r in range(64):
            for c in range(64):
                hf.data[r][c] = (100.0 + r * 2.0) / 350.0

        solver = SpatialConstraintSolver()
        footprint = solver.solve_placement(hf, wfc_dimensions=(4, 4), tile_size_meters=6.0)

        # Check center region was carved flat by solve_placement
        c_grid_x = int((footprint.center_world_cm[0] / 100.0) / hf.meters_per_cell)
        c_grid_y = int((footprint.center_world_cm[1] / 100.0) / hf.meters_per_cell)
        elev_center = hf.get_world_elevation_meters(c_grid_x, c_grid_y)
        assert abs(elev_center - footprint.pad_elevation_m) < 1.0

    def test_04_spatial_constraint_solver_road_generation(self):
        hf = Heightfield2D(
            width=64,
            height=64,
            meters_per_cell=4.0,
            min_elevation_meters=0.0,
            max_elevation_meters=350.0,
            initial_elevation=0.3,
        )
        solver = SpatialConstraintSolver()
        footprint = solver.solve_placement(hf, wfc_dimensions=(4, 4), tile_size_meters=6.0)

        assert footprint.entrance_airlock_cm[0] > 0
        assert footprint.entrance_airlock_cm[1] > 0
        assert footprint.road_terminus_coord[0] >= 0
        assert footprint.road_terminus_coord[1] >= 0
        assert footprint.facility_id == "facility_bunker_primary"

    def test_05_master_orchestrator_pipeline_small(self):
        cfg = VerticalSliceConfig(slice_name="Slice_Small_Test", size=SliceSize.SMALL, seed=7)
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        assert manifest.slice_name == "Slice_Small_Test"
        assert len(manifest.stage_metrics) == 8
        assert manifest.total_execution_time_s > 0.0
        assert manifest.total_execution_time_s < 10.0
        assert len(manifest.artifacts) >= 8

        stage_names = [m.stage for m in manifest.stage_metrics]
        assert OrchestrationStage.LANDSCAPE in stage_names
        assert OrchestrationStage.SPATIAL_SOLVER in stage_names
        assert OrchestrationStage.WFC_INTERIOR in stage_names
        assert OrchestrationStage.AI_SQUADS in stage_names
        assert OrchestrationStage.WEATHER_ATMOSPHERE in stage_names
        assert OrchestrationStage.CHAOS_DESTRUCTION in stage_names
        assert OrchestrationStage.AUDIO_METASOUNDS in stage_names
        assert OrchestrationStage.QA_AUDIT in stage_names

    def test_06_master_orchestrator_pipeline_medium(self):
        cfg = VerticalSliceConfig(
            slice_name="Slice_Medium_Test",
            size=SliceSize.MEDIUM,
            biome=WeatherBiomeType.VOLCANIC,
            seed=88,
        )
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        assert manifest.landscape_summary["resolution"] == 128
        assert manifest.landscape_summary["world_size_meters"] == 512.0
        assert manifest.weather_summary["biome"] == "VOLCANIC"
        assert manifest.interior_summary["wfc_dimensions"] == (8, 8)

    def test_07_subsystems_manifest_content(self):
        cfg = VerticalSliceConfig(slice_name="Slice_Content_Check", size=SliceSize.SMALL, seed=12)
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        assert "weightmap_layers" in manifest.landscape_summary
        assert manifest.interior_summary["total_tiles"] == 16
        assert manifest.ai_summary["squads_deployed"] == 2
        assert manifest.weather_summary["sun_lux"] > 0
        assert manifest.chaos_summary["total_fracture_pieces"] == 16
        assert manifest.audio_summary["bunker_rt60_seconds"] > 0
        assert manifest.qa_summary["playtest_outcome"] in ("VICTORY", "TIMEOUT", "DEATH", "SOFTLOCK")

    def test_08_selective_pipeline_disabling(self):
        cfg = VerticalSliceConfig(
            slice_name="Slice_No_Chaos_Audio",
            size=SliceSize.SMALL,
            enable_chaos_destruction=False,
            enable_metasounds_audio=False,
            seed=15,
        )
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        assert manifest.chaos_summary == {}
        assert manifest.audio_summary == {}
        assert manifest.landscape_summary["resolution"] == 64
        assert manifest.interior_summary["total_tiles"] == 16

    def test_09_package_integrator_directory_structure(self, temp_out_dir):
        cfg = VerticalSliceConfig(slice_name="Package_Test", size=SliceSize.SMALL, seed=42)
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        integrator = MasterPackageIntegrator()
        pkg = integrator.package_slice(manifest, output_dir=temp_out_dir, as_zip=False)

        assert pkg.bundle_directory == temp_out_dir
        assert len(pkg.files_written) >= 10
        assert os.path.exists(os.path.join(temp_out_dir, "slice_manifest.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "terrain", "heightfield.r16"))
        assert os.path.exists(os.path.join(temp_out_dir, "terrain", "landscape_weightmaps.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "spatial", "facility_placement.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "interior", "wfc_interior.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "ai", "ai_squads.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "weather", "weather_manifest.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "chaos", "chaos_destruction.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "audio", "metasounds_manifest.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "qa", "qa_playtest_report.json"))
        assert os.path.exists(os.path.join(temp_out_dir, "scripts", "import_full_vertical_slice.py"))

    def test_10_package_integrator_heightfield_r16_integrity(self, temp_out_dir):
        cfg = VerticalSliceConfig(slice_name="Heightfield_Test", size=SliceSize.SMALL, seed=42)
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        integrator = MasterPackageIntegrator()
        pkg = integrator.package_slice(manifest, output_dir=temp_out_dir)

        hf_path = os.path.join(temp_out_dir, "terrain", "heightfield.r16")
        expected_size = 64 * 64 * 2  # 8192 bytes
        assert os.path.getsize(hf_path) == expected_size

    def test_11_package_integrator_manifest_checksum(self, temp_out_dir):
        cfg = VerticalSliceConfig(slice_name="Checksum_Test", size=SliceSize.SMALL, seed=42)
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        integrator = MasterPackageIntegrator()
        pkg = integrator.package_slice(manifest, output_dir=temp_out_dir)

        assert len(pkg.manifest_checksum) == 64
        import hashlib
        with open(os.path.join(temp_out_dir, "slice_manifest.json"), "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        assert pkg.manifest_checksum == h

    def test_12_package_integrator_zip_archive(self, temp_out_dir):
        cfg = VerticalSliceConfig(slice_name="Zip_Test", size=SliceSize.SMALL, seed=42)
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        target_folder = os.path.join(temp_out_dir, "Zip_Slice")
        integrator = MasterPackageIntegrator()
        pkg = integrator.package_slice(manifest, output_dir=target_folder, as_zip=True)

        assert pkg.is_zip is True
        assert pkg.zip_path is not None
        assert os.path.exists(pkg.zip_path)

        with zipfile.ZipFile(pkg.zip_path, "r") as zf:
            namelist = zf.namelist()
            assert any("slice_manifest.json" in n for n in namelist)
            assert any("heightfield.r16" in n for n in namelist)
            assert any("import_full_vertical_slice.py" in n for n in namelist)

    def test_13_ue5_automation_script_syntax_and_standalone_run(self, temp_out_dir):
        cfg = VerticalSliceConfig(slice_name="Script_Exec_Test", size=SliceSize.SMALL, seed=42)
        orchestrator = VerticalSliceMasterOrchestrator()
        manifest = orchestrator.execute_pipeline(cfg)

        integrator = MasterPackageIntegrator()
        pkg = integrator.package_slice(manifest, output_dir=temp_out_dir)

        proc = subprocess.run(
            [sys.executable, pkg.ue5_script_path],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0
        assert "[AOE-Reconstruct]" in proc.stdout
        assert "Vertical slice 'Script_Exec_Test' successfully reconstructed" in proc.stdout

    def test_14_convenience_api_build_vertical_slice(self, temp_out_dir):
        cfg = VerticalSliceConfig(slice_name="Convenience_Slice", size=SliceSize.SMALL, seed=55)
        pkg = build_vertical_slice(config=cfg, output_dir=temp_out_dir, as_zip=False)

        assert isinstance(pkg, PackageResult)
        assert pkg.bundle_directory == temp_out_dir
        assert len(pkg.files_written) >= 10

    def test_15_slice_cli_parser_and_execution(self, temp_out_dir):
        parser = create_cli_parser()
        args = parser.parse_args([
            "--name", "CLI_Generated_Slice",
            "--size", "SMALL",
            "--biome", "ALPINE",
            "--seed", "777",
            "--output-dir", temp_out_dir,
        ])
        assert args.name == "CLI_Generated_Slice"
        assert args.size == "SMALL"
        assert args.biome == "ALPINE"
        assert args.seed == 777

        ret = run_cli([
            "--name", "CLI_Generated_Slice",
            "--size", "SMALL",
            "--biome", "ALPINE",
            "--seed", "777",
            "--output-dir", temp_out_dir,
        ])
        assert ret == 0
        assert os.path.exists(os.path.join(temp_out_dir, "slice_manifest.json"))

    def test_16_deterministic_reproducibility(self):
        cfg1 = VerticalSliceConfig(slice_name="Det_A", size=SliceSize.SMALL, seed=333)
        cfg2 = VerticalSliceConfig(slice_name="Det_B", size=SliceSize.SMALL, seed=333)

        orch = VerticalSliceMasterOrchestrator()
        m1 = orch.execute_pipeline(cfg1)
        m2 = orch.execute_pipeline(cfg2)

        assert m1.spatial_footprint.center_world_cm == m2.spatial_footprint.center_world_cm
        assert m1.weather_summary["sun_elevation_deg"] == m2.weather_summary["sun_elevation_deg"]
        assert m1.weather_summary["sun_lux"] == m2.weather_summary["sun_lux"]
        assert m1.interior_summary["total_tiles"] == m2.interior_summary["total_tiles"]
