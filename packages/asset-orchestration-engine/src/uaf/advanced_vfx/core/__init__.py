"""
UAF-81.89: Core exports.
"""

from .contracts import (
    FluidBoundaryCondition,
    AdvectionScheme,
    SkinningAlgorithm,
    SpectralBand,
    ShaderOptimizationLevel,
    DisplacementChannel,
    ensure_finite_scalar,
    ensure_finite_vec3,
    clamp_scalar,
    GridDimensions2D,
    GridDimensions3D,
    FluidProperties,
    CFLValidationResult,
    validate_cfl_condition,
    SkeletalBoneTransform,
    SkeletalVertex,
    SurfaceImpactEvent,
    VolumetricShadowSettings,
    DielectricBranchConfig,
    AudioBandEnvelope,
    ComputeShaderCode,
)
from .soa_buffer import ParticleSoABuffer

__all__ = [
    "FluidBoundaryCondition",
    "AdvectionScheme",
    "SkinningAlgorithm",
    "SpectralBand",
    "ShaderOptimizationLevel",
    "DisplacementChannel",
    "ensure_finite_scalar",
    "ensure_finite_vec3",
    "clamp_scalar",
    "GridDimensions2D",
    "GridDimensions3D",
    "FluidProperties",
    "CFLValidationResult",
    "validate_cfl_condition",
    "SkeletalBoneTransform",
    "SkeletalVertex",
    "SurfaceImpactEvent",
    "VolumetricShadowSettings",
    "DielectricBranchConfig",
    "AudioBandEnvelope",
    "ComputeShaderCode",
    "ParticleSoABuffer",
]
