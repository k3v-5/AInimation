"""
UAF-81.101: Core Contracts for Universal DCC & Engine Bridge Tools.
Defines Pydantic v2 specifications for UI parameter types, tool categories,
action schemas, execution results, and multi-engine palette manifests.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TargetEnvironment(str, Enum):
    """Target runtime environment for tool execution and UI hosting."""
    UNREAL_ENGINE_5 = "UNREAL_ENGINE_5"
    BLENDER = "BLENDER"
    UNIVERSAL = "UNIVERSAL"


class ParameterType(str, Enum):
    """User input control types for in-engine parameter editing."""
    FLOAT_SLIDER = "FLOAT_SLIDER"
    INT_SLIDER = "INT_SLIDER"
    DROPDOWN = "DROPDOWN"
    TOGGLE_BOOLEAN = "TOGGLE_BOOLEAN"
    STRING_INPUT = "STRING_INPUT"
    ACTION_BUTTON = "ACTION_BUTTON"


class ToolCategory(str, Enum):
    """Functional categorization of procedural generation actions."""
    LANDSCAPE_TERRAIN = "LANDSCAPE_TERRAIN"
    WFC_INTERIORS = "WFC_INTERIORS"
    WEATHER_ATMOSPHERE = "WEATHER_ATMOSPHERE"
    CHAOS_DESTRUCTION = "CHAOS_DESTRUCTION"
    AI_SQUADS = "AI_SQUADS"
    AUDIO_METASOUNDS = "AUDIO_METASOUNDS"
    QA_PLAYTEST = "QA_PLAYTEST"
    DCC_ASSET_TOOLS = "DCC_ASSET_TOOLS"


class ToolParameterSpec(BaseModel):
    """Specification of an interactive parameter exposed in DCC/Engine palettes."""
    param_id: str
    label: str
    param_type: ParameterType
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: List[str] = Field(default_factory=list)
    description: str = ""


class StudioActionSpec(BaseModel):
    """Declarative specification of a procedural generation command."""
    action_id: str
    name: str
    category: ToolCategory
    description: str
    target_environment: TargetEnvironment = TargetEnvironment.UNIVERSAL
    parameters: List[ToolParameterSpec] = Field(default_factory=list)
    endpoint: str = ""
    icon: str = "default_icon"

    def get_parameter(self, param_id: str) -> Optional[ToolParameterSpec]:
        for p in self.parameters:
            if p.param_id == param_id:
                return p
        return None


class ActionResult(BaseModel):
    """Execution feedback returned from procedural actions to in-engine tools."""
    action_id: str
    success: bool
    message: str
    artifacts_generated: List[str] = Field(default_factory=list)
    execution_time_s: float = 0.0
    output_data: Dict[str, Any] = Field(default_factory=dict)


class EnginePaletteManifest(BaseModel):
    """Full manifest describing an in-engine tool palette, tabs, and actions."""
    palette_id: str
    title: str
    environment: TargetEnvironment
    version: str = "1.0.0"
    categories: List[ToolCategory] = Field(default_factory=list)
    actions: List[StudioActionSpec] = Field(default_factory=list)
    dock_area: str = "Right"
    hotkey: str = "Ctrl+Shift+U"


def create_default_studio_actions() -> List[StudioActionSpec]:
    """Generates the universal catalog of standard AOE procedural generation actions."""
    return [
        StudioActionSpec(
            action_id="landscape_generate",
            name="Generate Macro Terrain & Biomes",
            category=ToolCategory.LANDSCAPE_TERRAIN,
            description="Generates continuous 2D heightfields with erosion and Whittaker biome weightmaps.",
            target_environment=TargetEnvironment.UNREAL_ENGINE_5,
            parameters=[
                ToolParameterSpec(param_id="seed", label="Noise Seed", param_type=ParameterType.INT_SLIDER, default_value=42, min_value=1, max_value=99999),
                ToolParameterSpec(param_id="resolution", label="Terrain Size", param_type=ParameterType.DROPDOWN, default_value="128", options=["64", "128", "256", "512", "1024"]),
                ToolParameterSpec(param_id="biome", label="Whittaker Biome", param_type=ParameterType.DROPDOWN, default_value="TEMPERATE_FOREST", options=["TEMPERATE_FOREST", "DESERT", "SWAMP", "ARCTIC", "ALPINE", "TUNDRA"]),
                ToolParameterSpec(param_id="erosion_steps", label="Hydraulic Erosion Iterations", param_type=ParameterType.INT_SLIDER, default_value=25, min_value=0, max_value=100),
            ],
            endpoint="uaf.landscape.generator",
        ),
        StudioActionSpec(
            action_id="wfc_generate_interior",
            name="Solve & Place WFC Modular Interior",
            category=ToolCategory.WFC_INTERIORS,
            description="Solves 2D/3D modular interior layouts with Lock-and-Key progression and zero softlocks.",
            target_environment=TargetEnvironment.UNREAL_ENGINE_5,
            parameters=[
                ToolParameterSpec(param_id="seed", label="WFC Seed", param_type=ParameterType.INT_SLIDER, default_value=101, min_value=1, max_value=99999),
                ToolParameterSpec(param_id="grid_width", label="Grid Width", param_type=ParameterType.INT_SLIDER, default_value=6, min_value=3, max_value=20),
                ToolParameterSpec(param_id="grid_height", label="Grid Height", param_type=ParameterType.INT_SLIDER, default_value=6, min_value=3, max_value=20),
                ToolParameterSpec(param_id="theme", label="Facility Theme", param_type=ParameterType.DROPDOWN, default_value="SCIFI_BUNKER", options=["SCIFI_BUNKER", "INDUSTRIAL_DEPOT", "RESEARCH_LAB"]),
                ToolParameterSpec(param_id="lock_key_progression", label="Generate Locked Doors & Keys", param_type=ParameterType.TOGGLE_BOOLEAN, default_value=True),
            ],
            endpoint="uaf.level_design.wfc",
        ),
        StudioActionSpec(
            action_id="weather_apply_state",
            name="Apply Dynamic Weather & Day/Night",
            category=ToolCategory.WEATHER_ATMOSPHERE,
            description="Controls Lumen lighting, celestial day/night trajectory, and dynamic weather presets.",
            target_environment=TargetEnvironment.UNREAL_ENGINE_5,
            parameters=[
                ToolParameterSpec(param_id="time_of_day", label="Time of Day (Hours)", param_type=ParameterType.FLOAT_SLIDER, default_value=12.0, min_value=0.0, max_value=24.0, step=0.5),
                ToolParameterSpec(param_id="precipitation", label="Precipitation Type", param_type=ParameterType.DROPDOWN, default_value="NONE", options=["NONE", "LIGHT_RAIN", "HEAVY_STORM", "SNOW", "BLIZZARD", "SANDSTORM"]),
                ToolParameterSpec(param_id="intensity", label="Rain/Snow Intensity", param_type=ParameterType.FLOAT_SLIDER, default_value=0.5, min_value=0.0, max_value=1.0, step=0.05),
                ToolParameterSpec(param_id="temperature", label="Ambient Temperature (°C)", param_type=ParameterType.FLOAT_SLIDER, default_value=20.0, min_value=-25.0, max_value=50.0, step=1.0),
            ],
            endpoint="uaf.weather_atmosphere.controller",
        ),
        StudioActionSpec(
            action_id="chaos_fracture_mesh",
            name="Fracture & Spawn GeometryCollection",
            category=ToolCategory.CHAOS_DESTRUCTION,
            description="Pre-fractures structural geometry using Voronoi partitioning and physics mass densities.",
            target_environment=TargetEnvironment.UNREAL_ENGINE_5,
            parameters=[
                ToolParameterSpec(param_id="material_type", label="Destruction Material", param_type=ParameterType.DROPDOWN, default_value="CONCRETE", options=["CONCRETE", "REINFORCED_METAL", "TEMPERED_GLASS", "MASONRY_BRICK"]),
                ToolParameterSpec(param_id="piece_count", label="Voronoi Piece Count", param_type=ParameterType.INT_SLIDER, default_value=16, min_value=4, max_value=64),
                ToolParameterSpec(param_id="anchor_mode", label="Anchor Stability Mode", param_type=ParameterType.DROPDOWN, default_value="BASE_GROUNDED", options=["BASE_GROUNDED", "TOP_SUPPORTED", "UNANCHORED"]),
            ],
            endpoint="uaf.chaos_destruction.compiler",
        ),
        StudioActionSpec(
            action_id="audio_deploy_metasounds",
            name="Deploy Adaptive MetaSounds Graph",
            category=ToolCategory.AUDIO_METASOUNDS,
            description="Configures Quartz-quantized adaptive music stems and topological room acoustics.",
            target_environment=TargetEnvironment.UNREAL_ENGINE_5,
            parameters=[
                ToolParameterSpec(param_id="pacing_phase", label="Dynamic Pacing Phase", param_type=ParameterType.DROPDOWN, default_value="CALM", options=["CALM", "BUILDUP", "PEAK", "COOLDOWN"]),
                ToolParameterSpec(param_id="rt60_decay_s", label="Target RT60 Decay (Seconds)", param_type=ParameterType.FLOAT_SLIDER, default_value=1.2, min_value=0.2, max_value=4.0, step=0.1),
            ],
            endpoint="uaf.interactive_audio.orchestrator",
        ),
        StudioActionSpec(
            action_id="playtest_run_simulation",
            name="Execute Headless AI Playtest Audit",
            category=ToolCategory.QA_PLAYTEST,
            description="Runs simulated gameplay bots to detect softlocks, unfair difficulty spikes, and traversal bottlenecks.",
            target_environment=TargetEnvironment.UNREAL_ENGINE_5,
            parameters=[
                ToolParameterSpec(param_id="archetype", label="Bot Playstyle", param_type=ParameterType.DROPDOWN, default_value="EXPLORER", options=["EXPLORER", "SPEEDRUNNER", "COMBATANT", "NOVICE", "COMPLETIONIST"]),
                ToolParameterSpec(param_id="max_ticks", label="Max Simulation Ticks", param_type=ParameterType.INT_SLIDER, default_value=500, min_value=100, max_value=2000),
            ],
            endpoint="uaf.playtesting.agent",
        ),
        StudioActionSpec(
            action_id="blender_inspect_mesh",
            name="Inspect Mesh Topology & Collision Bounds",
            category=ToolCategory.DCC_ASSET_TOOLS,
            description="Verifies manifold geometry, vertex normals, pivot alignment at origin, and bounding bounds.",
            target_environment=TargetEnvironment.BLENDER,
            parameters=[
                ToolParameterSpec(param_id="check_manifold", label="Enforce Watertight Manifold", param_type=ParameterType.TOGGLE_BOOLEAN, default_value=True),
                ToolParameterSpec(param_id="check_pivot", label="Enforce Pivot at (0,0,0)", param_type=ParameterType.TOGGLE_BOOLEAN, default_value=True),
            ],
            endpoint="uaf.blender.inspector",
        ),
        StudioActionSpec(
            action_id="blender_export_ue5_fbx",
            name="Export FBX to UE5 Standards",
            category=ToolCategory.DCC_ASSET_TOOLS,
            description="Exports selected mesh with applied transforms, metric scale (100cm), Z-up, and zero self-collision metadata.",
            target_environment=TargetEnvironment.BLENDER,
            parameters=[
                ToolParameterSpec(param_id="apply_transforms", label="Apply Location/Rotation/Scale", param_type=ParameterType.TOGGLE_BOOLEAN, default_value=True),
                ToolParameterSpec(param_id="scale_factor", label="Unit Scale Multiplier", param_type=ParameterType.FLOAT_SLIDER, default_value=100.0, min_value=1.0, max_value=100.0),
            ],
            endpoint="uaf.blender.exporter",
        ),
    ]
