"""
Acceptance Test Suite for UAF-81.101: Universal DCC & Engine Bridge Tools.
Validates Pydantic v2 contracts, standard action catalog, UE5 Python palette generation,
Blender N-Panel addon generation, parameter validation, action dispatcher routing,
and zero-project-coupling portability across any Unreal Engine 5 project or Blender setup.
"""

import ast
import json
import tempfile
from pathlib import Path
import pytest

from uaf.engine_tools import (
    TargetEnvironment,
    ParameterType,
    ToolCategory,
    ToolParameterSpec,
    StudioActionSpec,
    ActionResult,
    EnginePaletteManifest,
    create_default_studio_actions,
    UE5StudioPaletteGenerator,
    BlenderStudioPanelGenerator,
    StudioActionDispatcher,
)


class TestAcceptanceUAF81_101:

    def test_uaf81_101_contracts_and_models(self):
        """Validates all Pydantic v2 models with keyword arguments."""
        param = ToolParameterSpec(
            param_id="test_slider",
            label="Test Slider",
            param_type=ParameterType.FLOAT_SLIDER,
            default_value=5.0,
            min_value=0.0,
            max_value=10.0,
            step=0.5,
            description="A test slider parameter",
        )
        assert param.param_id == "test_slider"
        assert param.min_value == 0.0

        action = StudioActionSpec(
            action_id="custom_action",
            name="Custom Action",
            category=ToolCategory.LANDSCAPE_TERRAIN,
            description="A custom test action",
            target_environment=TargetEnvironment.UNIVERSAL,
            parameters=[param],
        )
        assert action.get_parameter("test_slider") is not None
        assert action.get_parameter("non_existent") is None

        res = ActionResult(
            action_id="custom_action",
            success=True,
            message="Completed",
            artifacts_generated=["test_artifact.json"],
            execution_time_s=0.05,
        )
        assert res.success is True
        assert len(res.artifacts_generated) == 1

    def test_uaf81_101_default_actions_catalog(self):
        """Validates default catalog contains actions across all key domains."""
        actions = create_default_studio_actions()
        assert len(actions) == 8

        cat_set = {a.category for a in actions}
        assert ToolCategory.LANDSCAPE_TERRAIN in cat_set
        assert ToolCategory.WFC_INTERIORS in cat_set
        assert ToolCategory.WEATHER_ATMOSPHERE in cat_set
        assert ToolCategory.CHAOS_DESTRUCTION in cat_set
        assert ToolCategory.AUDIO_METASOUNDS in cat_set
        assert ToolCategory.QA_PLAYTEST in cat_set
        assert ToolCategory.DCC_ASSET_TOOLS in cat_set

        for a in actions:
            assert len(a.action_id) > 0
            assert len(a.name) > 0
            assert len(a.description) > 0
            assert len(a.parameters) > 0

    def test_uaf81_101_ue5_palette_manifest_generation(self):
        """Validates UE5 palette manifest generation filters Blender-only actions."""
        gen = UE5StudioPaletteGenerator()
        manifest = gen.generate_manifest()

        assert manifest.environment == TargetEnvironment.UNREAL_ENGINE_5
        assert len(manifest.actions) > 0

        # Verify Blender-only actions are excluded
        for act in manifest.actions:
            assert act.target_environment in (TargetEnvironment.UNREAL_ENGINE_5, TargetEnvironment.UNIVERSAL)
            assert act.action_id not in ("blender_inspect_mesh", "blender_export_ue5_fbx")

        # Verify categories are properly populated
        assert ToolCategory.LANDSCAPE_TERRAIN in manifest.categories
        assert ToolCategory.WEATHER_ATMOSPHERE in manifest.categories

    def test_uaf81_101_ue5_palette_script_generation_and_ast(self):
        """Validates that generated UE5 palette Python script is syntactically valid."""
        gen = UE5StudioPaletteGenerator()
        manifest = gen.generate_manifest()
        script_code = gen.generate_python_script(manifest)

        # Parse AST to ensure valid Python code
        parsed_ast = ast.parse(script_code)
        assert parsed_ast is not None

        # Verify key classes and methods are in the generated script
        assert "AOEStudioPaletteController" in script_code
        assert "register_palette_menu" in script_code
        assert "open_palette_window" in script_code
        assert "LevelEditor.MainMenu.Window" in script_code

    def test_uaf81_101_ue5_palette_export(self):
        """Validates export of UE5 palette manifest and Python tool script."""
        gen = UE5StudioPaletteGenerator()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_p = Path(tmpdir)
            exported = gen.export_tool(out_p)

            assert exported["manifest"].exists()
            assert exported["script"].exists()

            with open(exported["manifest"], "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["palette_id"] == "ue5_aoe_palette"
            assert data["environment"] == TargetEnvironment.UNREAL_ENGINE_5.value

    def test_uaf81_101_blender_panel_manifest_generation(self):
        """Validates Blender panel manifest filters out UE5-only actions."""
        gen = BlenderStudioPanelGenerator()
        manifest = gen.generate_manifest()

        assert manifest.environment == TargetEnvironment.BLENDER
        for act in manifest.actions:
            assert act.target_environment in (TargetEnvironment.BLENDER, TargetEnvironment.UNIVERSAL)

        act_ids = [a.action_id for a in manifest.actions]
        assert "blender_inspect_mesh" in act_ids
        assert "blender_export_ue5_fbx" in act_ids

    def test_uaf81_101_blender_addon_script_generation_and_ast(self):
        """Validates that generated Blender addon script has valid AST and operators."""
        gen = BlenderStudioPanelGenerator()
        manifest = gen.generate_manifest()
        addon_code = gen.generate_addon_script(manifest)

        # Parse AST
        parsed_ast = ast.parse(addon_code)
        assert parsed_ast is not None

        # Verify blender addon structures
        assert "bl_info" in addon_code
        assert "AOE_OT_VerifyMeshMetrics" in addon_code
        assert "AOE_OT_ExportUE5FBX" in addon_code
        assert "AOE_PT_StudioPanel" in addon_code
        assert "VIEW3D_PT_aoe_studio" in addon_code

    def test_uaf81_101_blender_addon_export(self):
        """Validates export of Blender addon script and manifest."""
        gen = BlenderStudioPanelGenerator()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_p = Path(tmpdir)
            exported = gen.export_addon(out_p)

            assert exported["manifest"].exists()
            assert exported["addon"].exists()

            with open(exported["manifest"], "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["palette_id"] == "blender_aoe_panel"
            assert data["environment"] == TargetEnvironment.BLENDER.value

    def test_uaf81_101_dispatcher_registration_and_listing(self):
        """Validates action registration and category filtering in dispatcher."""
        dispatcher = StudioActionDispatcher()
        all_actions = dispatcher.list_actions()
        assert len(all_actions) >= 8

        landscape_actions = dispatcher.list_actions(ToolCategory.LANDSCAPE_TERRAIN)
        assert len(landscape_actions) == 1
        assert landscape_actions[0].action_id == "landscape_generate"

        dcc_actions = dispatcher.list_actions(ToolCategory.DCC_ASSET_TOOLS)
        assert len(dcc_actions) == 2

    def test_uaf81_101_dispatcher_parameter_validation_bounds(self):
        """Verifies parameter bounds checking and error handling."""
        dispatcher = StudioActionDispatcher()

        # Numeric out of bounds (min is 1)
        res_low = dispatcher.dispatch("landscape_generate", {"seed": 0})
        assert res_low.success is False
        assert "min allowed" in res_low.message

        # Dropdown invalid option
        res_opt = dispatcher.dispatch("landscape_generate", {"biome": "TROPICAL_JUNGLE_INVALID"})
        assert res_opt.success is False
        assert "not in allowed options" in res_opt.message

        # Unknown action
        res_unknown = dispatcher.dispatch("non_existent_action_123")
        assert res_unknown.success is False
        assert "not found in registry" in res_unknown.message

    def test_uaf81_101_dispatcher_landscape_generation(self):
        """Tests dispatcher execution of landscape generation."""
        dispatcher = StudioActionDispatcher()
        res = dispatcher.dispatch(
            "landscape_generate",
            {"seed": 999, "resolution": "256", "biome": "DESERT", "erosion_steps": 30},
        )
        assert res.success is True
        assert "Generated 256x256 landscape" in res.message
        assert res.output_data["seed"] == 999
        assert res.output_data["resolution"] == 256
        assert len(res.artifacts_generated) == 2

    def test_uaf81_101_dispatcher_wfc_interior_generation(self):
        """Tests dispatcher execution of WFC interior generation."""
        dispatcher = StudioActionDispatcher()
        res = dispatcher.dispatch(
            "wfc_generate_interior",
            {"seed": 555, "grid_width": 8, "grid_height": 8, "theme": "RESEARCH_LAB", "lock_key_progression": True},
        )
        assert res.success is True
        assert res.output_data["total_tiles"] == 64
        assert res.output_data["theme"] == "RESEARCH_LAB"
        assert res.output_data["locked_doors"] == 2

    def test_uaf81_101_dispatcher_weather_atmosphere_transition(self):
        """Tests dispatcher execution of dynamic weather / day-night transition."""
        dispatcher = StudioActionDispatcher()
        res = dispatcher.dispatch(
            "weather_apply_state",
            {"time_of_day": 18.0, "precipitation": "HEAVY_STORM", "intensity": 0.8, "temperature": 15.0},
        )
        assert res.success is True
        assert res.output_data["time_of_day_hours"] == 18.0
        assert res.output_data["precipitation"] == "HEAVY_STORM"
        assert "sun_elevation_deg" in res.output_data
        assert "ev100" in res.output_data

    def test_uaf81_101_dispatcher_chaos_and_playtest_actions(self):
        """Tests dispatcher execution of Chaos fracturing and QA playtest simulation."""
        dispatcher = StudioActionDispatcher()

        res_chaos = dispatcher.dispatch(
            "chaos_fracture_mesh",
            {"material_type": "REINFORCED_METAL", "piece_count": 32, "anchor_mode": "BASE_GROUNDED"},
        )
        assert res_chaos.success is True
        assert res_chaos.output_data["pieces_fractured"] == 32
        assert res_chaos.output_data["macro_chunks"] == 16

        res_qa = dispatcher.dispatch(
            "playtest_run_simulation",
            {"archetype": "SPEEDRUNNER", "max_ticks": 800},
        )
        assert res_qa.success is True
        assert res_qa.output_data["archetype"] == "SPEEDRUNNER"
        assert res_qa.output_data["softlocks_detected"] == 0

    def test_uaf81_101_dispatcher_custom_action_handler(self):
        """Verifies registering a custom user procedural action handler."""
        dispatcher = StudioActionDispatcher()

        custom_action = StudioActionSpec(
            action_id="custom_pipeline_step",
            name="Custom Procedural Step",
            category=ToolCategory.LANDSCAPE_TERRAIN,
            description="Custom step for project",
        )

        def custom_handler(params):
            return ActionResult(
                action_id="custom_pipeline_step",
                success=True,
                message="Custom execution successful!",
                output_data={"custom_key": 42},
            )

        dispatcher.register_action(custom_action, handler=custom_handler)
        res = dispatcher.dispatch("custom_pipeline_step")
        assert res.success is True
        assert res.output_data["custom_key"] == 42
        assert res.execution_time_s >= 0.0

    def test_uaf81_101_zero_project_coupling_portability(self):
        """
        Enforces zero hardcoded project paths across all manifests and tool scripts.
        Guarantees that AOE functions as a universal engine usable by any UE5/Blender project.
        """
        ue5_gen = UE5StudioPaletteGenerator()
        blender_gen = BlenderStudioPanelGenerator()

        ue5_script = ue5_gen.generate_python_script(ue5_gen.generate_manifest())
        blender_addon = blender_gen.generate_addon_script(blender_gen.generate_manifest())

        forbidden_strings = [
            "Darx_Proyect",
            "DarX",
            r"C:\Users",
            r"E:\Darx",
            "/Game/Darx",
        ]

        for forbidden in forbidden_strings:
            assert forbidden not in ue5_script, f"Found hardcoded project string '{forbidden}' in UE5 palette script!"
            assert forbidden not in blender_addon, f"Found hardcoded project string '{forbidden}' in Blender addon!"
