"""
Universal Asset Factory (UAF) - Asset Intelligence & Specification (UAF-81.1)
"""

from .models import (
    ComplexityLevel,
    SemanticAsset,
    CharacterSemanticModel,
    ANATOMICAL_REGIONS,
    MaterialSemanticModel,
    MaterialLayer,
    TextureSetSemanticModel,
    TextureMapSpecification,
    ModularKitSemanticModel,
    ModularModule,
    ConnectionSocket,
    EnvironmentSemanticModel,
    WorldSemanticModel,
    LevelSemanticModel,
)

from .archetypes import AssetArchetype, ArchetypeRegistry
from .parameters import ParameterType, ParameterProvenance, ParameterMetadata, UnitNormalizer
from .constraints import (
    ConstraintCategory,
    ConstraintType,
    AssetConstraint,
    ConstraintResolver,
    ResolutionTraceEntry,
    ConflictReport,
)
from .dependencies import DependencyGraph, CyclicDependencyError
from .profiles import StyleProfile, QualityProfile, TargetProfile
from .blueprint import BlueprintNode, AssetBlueprint
from .compiler import (
    ResolvedAssetSpecification,
    CapabilityGapReport,
    ResolutionPipeline,
    SpecificationMigrator,
)

__all__ = [
    "ComplexityLevel",
    "SemanticAsset",
    "CharacterSemanticModel",
    "ANATOMICAL_REGIONS",
    "MaterialSemanticModel",
    "MaterialLayer",
    "TextureSetSemanticModel",
    "TextureMapSpecification",
    "ModularKitSemanticModel",
    "ModularModule",
    "ConnectionSocket",
    "EnvironmentSemanticModel",
    "WorldSemanticModel",
    "LevelSemanticModel",
    "AssetArchetype",
    "ArchetypeRegistry",
    "ParameterType",
    "ParameterProvenance",
    "ParameterMetadata",
    "UnitNormalizer",
    "ConstraintCategory",
    "ConstraintType",
    "AssetConstraint",
    "ConstraintResolver",
    "ResolutionTraceEntry",
    "ConflictReport",
    "DependencyGraph",
    "CyclicDependencyError",
    "StyleProfile",
    "QualityProfile",
    "TargetProfile",
    "BlueprintNode",
    "AssetBlueprint",
    "ResolvedAssetSpecification",
    "CapabilityGapReport",
    "ResolutionPipeline",
    "SpecificationMigrator",
]
