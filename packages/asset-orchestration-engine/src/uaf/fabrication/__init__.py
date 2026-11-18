"""
Universal Asset Factory (UAF) - Procedural Character Fabrication & High-Complexity Geometry (UAF-81.10)
"""

from .anatomy import (
    ProportionProfileType,
    ParametricAnatomy,
    ProportionProfile,
    FormLevel,
    BodyComponent,
    SemanticBodyGraph,
)

from .garments import (
    GarmentLayer,
    GarmentDefinition,
)

from .generator import (
    TopologyStrategyType,
    FabricationQuality,
    ProceduralCharacterFabricator,
)

from .validation import (
    FabricationQualityScore,
    FabricationValidationReport,
    FabricationValidator,
)

from .package import (
    FabricatedCharacterPackage,
)

__all__ = [
    "ProportionProfileType",
    "ParametricAnatomy",
    "ProportionProfile",
    "FormLevel",
    "BodyComponent",
    "SemanticBodyGraph",
    "GarmentLayer",
    "GarmentDefinition",
    "TopologyStrategyType",
    "FabricationQuality",
    "ProceduralCharacterFabricator",
    "FabricationQualityScore",
    "FabricationValidationReport",
    "FabricationValidator",
    "FabricatedCharacterPackage",
]
