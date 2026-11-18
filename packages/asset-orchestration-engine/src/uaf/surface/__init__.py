"""
Universal Asset Factory (UAF) - Material, Texture & Surface Authoring Fabric (UAF-81.4)
"""

from .models import (
    PBRChannel,
    ColorSpace,
    ShaderModel,
    ChannelPacking,
    PhysicalClass,
    TextureDefinition,
    TextureSource,
    MaskType,
    MaskSource,
    BlendMode,
    SurfaceMask,
    MaterialLayer,
    MaterialDefinition,
    MaterialInstance,
    SemanticSurfaceRole,
    SurfaceDefinition,
    TexelDensityProfile,
    TextureSet,
    SurfacePackage,
)

from .families import MaterialFamily, MaterialFamilyRegistry

from .baking import BakeType, BakePlan, BakeResult, BakeEngine

from .validation import (
    SurfaceValidator,
    SurfaceValidationReport,
    SurfaceQualityScore,
    QualityTier,
    SurfaceQualityReport,
    ComprehensiveSurfaceValidator,
)

from .graph import SurfaceDependencyTracker

from .generators import SurfaceSynthesizer, UnrealSurfacePackage

from .uv import (
    UVChannel,
    UVStrategy,
    UVOverlapPolicy,
    UVDefinition,
    TrimRegion,
    TrimSheetDefinition,
    TextureAtlasDefinition,
    UDIMDefinition,
)

from .synthesis import (
    ProceduralPatternType,
    ProceduralTextureSynthesizer,
)

__all__ = [
    "PBRChannel",
    "ColorSpace",
    "ShaderModel",
    "ChannelPacking",
    "PhysicalClass",
    "TextureDefinition",
    "TextureSource",
    "MaskType",
    "MaskSource",
    "BlendMode",
    "SurfaceMask",
    "MaterialLayer",
    "MaterialDefinition",
    "MaterialInstance",
    "SemanticSurfaceRole",
    "SurfaceDefinition",
    "TexelDensityProfile",
    "TextureSet",
    "SurfacePackage",
    "MaterialFamily",
    "MaterialFamilyRegistry",
    "BakeType",
    "BakePlan",
    "BakeResult",
    "BakeEngine",
    "SurfaceValidator",
    "SurfaceValidationReport",
    "SurfaceQualityScore",
    "QualityTier",
    "SurfaceQualityReport",
    "ComprehensiveSurfaceValidator",
    "SurfaceDependencyTracker",
    "SurfaceSynthesizer",
    "UnrealSurfacePackage",
    "UVChannel",
    "UVStrategy",
    "UVOverlapPolicy",
    "UVDefinition",
    "TrimRegion",
    "TrimSheetDefinition",
    "TextureAtlasDefinition",
    "UDIMDefinition",
    "ProceduralPatternType",
    "ProceduralTextureSynthesizer",
]

