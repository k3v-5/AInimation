"""
UAF-81.89: Core Contracts, Mathematical Foundations & Numerical Safety.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FluidBoundaryCondition(str, Enum):
    DIRICHLET = "DIRICHLET"
    NEUMANN = "NEUMANN"
    PERIODIC = "PERIODIC"
    OPEN = "OPEN"


class AdvectionScheme(str, Enum):
    SEMI_LAGRANGIAN = "SEMI_LAGRANGIAN"
    MACCORMACK_BFECC = "MACCORMACK_BFECC"


class SkinningAlgorithm(str, Enum):
    LINEAR_BLEND = "LINEAR_BLEND"
    DUAL_QUATERNION = "DUAL_QUATERNION"


class SpectralBand(str, Enum):
    SUB_BASS = "SUB_BASS"      # 20 - 60 Hz
    BASS = "BASS"              # 60 - 250 Hz
    LOW_MID = "LOW_MID"        # 250 - 500 Hz
    MID = "MID"                # 500 - 2000 Hz
    HIGH = "HIGH"              # 2000 - 8000 Hz
    AIR = "AIR"                # > 8000 Hz


class ShaderOptimizationLevel(str, Enum):
    O0_DEBUG = "O0_DEBUG"
    O1_BASIC = "O1_BASIC"
    O2_FAST_MATH = "O2_FAST_MATH"
    O3_AGGRESSIVE = "O3_AGGRESSIVE"


class DisplacementChannel(str, Enum):
    BURN = "BURN"
    LIQUID = "LIQUID"
    SNOW = "SNOW"
    MUD = "MUD"


# ---------------------------------------------------------------------------
# Numerical Safety Utilities
# ---------------------------------------------------------------------------

def ensure_finite_scalar(val: float, fallback: float = 0.0) -> float:
    """Ensure a scalar is finite and not NaN or inf."""
    if math.isnan(val) or math.isinf(val):
        return fallback
    return val


def ensure_finite_vec3(v: Tuple[float, float, float], fallback: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Tuple[float, float, float]:
    """Ensure a 3-tuple is finite."""
    return (
        ensure_finite_scalar(v[0], fallback[0]),
        ensure_finite_scalar(v[1], fallback[1]),
        ensure_finite_scalar(v[2], fallback[2]),
    )


def clamp_scalar(val: float, min_val: float, max_val: float) -> float:
    """Clamp a scalar within [min_val, max_val]."""
    if val < min_val:
        return min_val
    if val > max_val:
        return max_val
    return val


# ---------------------------------------------------------------------------
# Core Domain Models
# ---------------------------------------------------------------------------

class GridDimensions2D(BaseModel):
    width: int = Field(gt=0, description="Grid width in cells")
    height: int = Field(gt=0, description="Grid height in cells")
    cell_size: float = Field(gt=0.0, default=1.0, description="Physical size per cell in meters")


class GridDimensions3D(BaseModel):
    width: int = Field(gt=0, description="Grid width in cells (X)")
    height: int = Field(gt=0, description="Grid height in cells (Y)")
    depth: int = Field(gt=0, description="Grid depth in cells (Z)")
    cell_size: float = Field(gt=0.0, default=1.0, description="Physical size per cell in meters")


class FluidProperties(BaseModel):
    density: float = Field(default=1.0, gt=0.0, description="Fluid reference density kg/m3")
    viscosity: float = Field(default=0.0001, ge=0.0, description="Kinematic viscosity")
    buoyancy_alpha: float = Field(default=0.05, ge=0.0, description="Smoke weight coefficient")
    buoyancy_beta: float = Field(default=0.1, ge=0.0, description="Thermal expansion coefficient")
    ambient_temp: float = Field(default=20.0, description="Ambient temperature in Celsius")
    vorticity_epsilon: float = Field(default=0.5, ge=0.0, description="Vorticity confinement strength")


class CFLValidationResult(BaseModel):
    cfl_number: float
    is_stable: bool
    recommended_substeps: int
    max_velocity: float


def validate_cfl_condition(
    max_velocity: float,
    cell_size: float,
    dt: float,
    max_cfl: float = 1.0,
) -> CFLValidationResult:
    """
    Computes CFL = (v_max * dt) / dx and determines whether substeps are required.
    """
    safe_v = max(0.0001, abs(max_velocity))
    safe_dx = max(0.0001, cell_size)
    safe_dt = max(0.00001, dt)
    cfl = (safe_v * safe_dt) / safe_dx
    is_stable = cfl <= max_cfl
    substeps = max(1, math.ceil(cfl / max_cfl)) if not is_stable else 1
    return CFLValidationResult(
        cfl_number=cfl,
        is_stable=is_stable,
        recommended_substeps=substeps,
        max_velocity=safe_v,
    )


class SkeletalBoneTransform(BaseModel):
    bone_index: int
    name: str
    position: Tuple[float, float, float]
    rotation_quaternion: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0) # x,y,z,w
    linear_velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    angular_velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)


class SkeletalVertex(BaseModel):
    position: Tuple[float, float, float]
    normal: Tuple[float, float, float]
    uv: Tuple[float, float] = (0.0, 0.0)
    bone_indices: Tuple[int, int, int, int] = (0, 0, 0, 0)
    bone_weights: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)


class SurfaceImpactEvent(BaseModel):
    world_position: Tuple[float, float, float]
    normal: Tuple[float, float, float]
    radius: float = Field(gt=0.0, default=1.0)
    intensity: float = Field(ge=0.0, default=1.0)
    channel: DisplacementChannel = DisplacementChannel.BURN
    duration: float = Field(gt=0.0, default=5.0)


class VolumetricShadowSettings(BaseModel):
    absorption_coefficient: float = Field(default=0.5, ge=0.0)
    scattering_coefficient: float = Field(default=0.2, ge=0.0)
    step_size: float = Field(default=0.5, gt=0.0)
    num_slices: int = Field(default=32, gt=0)


class DielectricBranchConfig(BaseModel):
    source_pos: Tuple[float, float, float]
    target_pos: Tuple[float, float, float]
    breakdown_eta: float = Field(default=2.5, gt=0.0, description="NPW power law exponent")
    roughness: float = Field(default=0.35, ge=0.0, le=1.0)
    branch_probability: float = Field(default=0.25, ge=0.0, le=1.0)
    max_recursion: int = Field(default=4, ge=1, le=10)


class AudioBandEnvelope(BaseModel):
    band: SpectralBand
    frequency_range_hz: Tuple[float, float]
    current_energy: float = 0.0
    peak_energy: float = 0.0
    adsr_value: float = 0.0


class ComputeShaderCode(BaseModel):
    entry_point: str
    hlsl_source: str
    num_threads: Tuple[int, int, int] = (64, 1, 1)
    optimization_level: ShaderOptimizationLevel = ShaderOptimizationLevel.O2_FAST_MATH
    input_buffers: List[str] = Field(default_factory=list)
    output_buffers: List[str] = Field(default_factory=list)
