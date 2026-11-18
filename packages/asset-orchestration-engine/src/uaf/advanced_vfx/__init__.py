"""
UAF-81.89: Advanced Next-Gen VFX, Fluid Simulation & Environmental Coupling System.
"""

from .core import (
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
    ParticleSoABuffer,
)
from .fluids import (
    EulerianFluidGrid2D,
    EulerianFluidGrid3D,
    SmokeFireSolver,
)
from .geometry import (
    SkeletalMeshSampler,
    FractureChunk,
    FractureDebrisParticle,
    FractureVFXCoupler,
)
from .environment import (
    PersistentSurfaceManager,
    FoliageInteractionBuffer,
)
from .volumetrics import (
    DeepShadowMapper,
    EmissiveParticle,
    VirtualPointLight,
    ParticleLightManager,
)
from .optics import (
    LightningSegment,
    LightningBolt,
    DielectricBreakdownSolver,
    RefractiveShockwave,
    OpticalDistortionBuffer,
)
from .audio_reactive import (
    ADSREnvelope,
    AudioSpectralCoupler,
    BAND_FREQUENCIES,
)
from .compiler import (
    ASTNode,
    VFXJITCompiler,
)
from .bridge import (
    AdvancedNiagaraBridge,
)

__all__ = [
    # Core
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
    # Fluids
    "EulerianFluidGrid2D",
    "EulerianFluidGrid3D",
    "SmokeFireSolver",
    # Geometry
    "SkeletalMeshSampler",
    "FractureChunk",
    "FractureDebrisParticle",
    "FractureVFXCoupler",
    # Environment
    "PersistentSurfaceManager",
    "FoliageInteractionBuffer",
    # Volumetrics
    "DeepShadowMapper",
    "EmissiveParticle",
    "VirtualPointLight",
    "ParticleLightManager",
    # Optics
    "LightningSegment",
    "LightningBolt",
    "DielectricBreakdownSolver",
    "RefractiveShockwave",
    "OpticalDistortionBuffer",
    # Audio Reactive
    "ADSREnvelope",
    "AudioSpectralCoupler",
    "BAND_FREQUENCIES",
    # Compiler
    "ASTNode",
    "VFXJITCompiler",
    # Bridge
    "AdvancedNiagaraBridge",
]
