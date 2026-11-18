"""
UAF-81.102: Core Contracts for One-Click Full Vertical Slice Builder.
Defines Pydantic v2 schemas for master slice configuration, spatial placement,
pipeline stages, execution metrics, and the integrated root slice manifest.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.weather_atmosphere.core.contracts import WeatherBiomeType


class SliceTheme(str, Enum):
    """Aesthetic and structural theme for vertical slice facilities and props."""
    SCIFI_BUNKER = "SCIFI_BUNKER"
    RESEARCH_LAB = "RESEARCH_LAB"
    INDUSTRIAL_OUTPOST = "INDUSTRIAL_OUTPOST"
    ANCIENT_RUINS = "ANCIENT_RUINS"


class SliceDifficulty(str, Enum):
    """Global difficulty setting regulating enemy density, power budget, and loot tiers."""
    NOVICE = "NOVICE"
    BALANCED = "BALANCED"
    VETERAN = "VETERAN"
    NIGHTMARE = "NIGHTMARE"


class SliceSize(str, Enum):
    """World dimensions for the vertical slice."""
    SMALL = "SMALL"      # 64x64 landscape, 4x4 WFC
    MEDIUM = "MEDIUM"    # 128x128 landscape, 8x8 WFC
    LARGE = "LARGE"      # 256x256 landscape, 12x12 WFC

    @property
    def landscape_resolution(self) -> int:
        if self == SliceSize.SMALL:
            return 64
        elif self == SliceSize.MEDIUM:
            return 128
        return 256

    @property
    def wfc_grid_dimension(self) -> int:
        if self == SliceSize.SMALL:
            return 4
        elif self == SliceSize.MEDIUM:
            return 8
        return 12


class OrchestrationStage(str, Enum):
    """Discrete sequential stages executed by the master orchestrator."""
    LANDSCAPE = "LANDSCAPE"
    SPATIAL_SOLVER = "SPATIAL_SOLVER"
    WFC_INTERIOR = "WFC_INTERIOR"
    AI_SQUADS = "AI_SQUADS"
    WEATHER_ATMOSPHERE = "WEATHER_ATMOSPHERE"
    CHAOS_DESTRUCTION = "CHAOS_DESTRUCTION"
    AUDIO_METASOUNDS = "AUDIO_METASOUNDS"
    QA_AUDIT = "QA_AUDIT"
    PACKAGING = "PACKAGING"


class SpatialFootprint(BaseModel):
    """Geometric placement and leveling bounds for interior facility on the landscape."""
    facility_id: str = "facility_bunker"
    center_world_cm: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    grid_origin_coord: Tuple[int, int] = (0, 0)
    footprint_cells_x: int = 16
    footprint_cells_y: int = 16
    pad_elevation_m: float = 50.0
    entrance_airlock_cm: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    road_terminus_coord: Tuple[int, int] = (0, 0)
    safety_buffer_cm: float = 30.0  # Zero-clipping mathematical buffer


class VerticalSliceConfig(BaseModel):
    """Master configuration controlling the 1-click vertical slice production."""
    slice_name: str = "VS_SectorAlpha"
    seed: int = 42
    theme: SliceTheme = SliceTheme.SCIFI_BUNKER
    biome: WeatherBiomeType = WeatherBiomeType.TEMPERATE_FOREST
    size: SliceSize = SliceSize.MEDIUM
    difficulty: SliceDifficulty = SliceDifficulty.BALANCED
    time_of_day_hours: float = Field(default=14.0, ge=0.0, le=24.0)
    enable_chaos_destruction: bool = True
    enable_metasounds_audio: bool = True
    enable_ai_patrols: bool = True
    output_dir: str = "export/vertical_slice"


class StageExecutionMetric(BaseModel):
    """Telemetry recorded for a single stage in the orchestration pipeline."""
    stage: OrchestrationStage
    duration_s: float
    status: str = "SUCCESS"
    details: Dict[str, Any] = Field(default_factory=dict)


class IntegratedSliceManifest(BaseModel):
    """Root deliverable manifest bundling all subsystem outputs and QA verification data."""
    slice_name: str
    config: VerticalSliceConfig
    spatial_footprint: SpatialFootprint
    landscape_summary: Dict[str, Any] = Field(default_factory=dict)
    interior_summary: Dict[str, Any] = Field(default_factory=dict)
    ai_summary: Dict[str, Any] = Field(default_factory=dict)
    weather_summary: Dict[str, Any] = Field(default_factory=dict)
    chaos_summary: Dict[str, Any] = Field(default_factory=dict)
    audio_summary: Dict[str, Any] = Field(default_factory=dict)
    qa_summary: Dict[str, Any] = Field(default_factory=dict)
    stage_metrics: List[StageExecutionMetric] = Field(default_factory=list)
    total_execution_time_s: float = 0.0
    artifacts: List[str] = Field(default_factory=list)
