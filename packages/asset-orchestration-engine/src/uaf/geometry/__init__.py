"""
Universal Asset Factory (UAF) - Procedural Geometry & Asset Construction Fabric (UAF-81.3)
"""

from .models import (
    MultiResLevel,
    DetailRepresentation,
    DetailPolicy,
    Transform3D,
    AABB,
    BoundingSphere,
    MeshData,
    GeometryComponent,
)

from .modifiers import ModifierType, ProceduralModifier, ModifierStack

from .anatomy import (
    LandmarkSystem,
    STANDARD_LANDMARKS,
    AnatomyProfile,
    AttachmentSocket,
    ClothingLayerSystem,
    LayerClearanceReport,
    LAYER_HIERARCHY,
)

from .processing import (
    TopologyProcessor,
    TopologyReport,
    UVGenerator,
    UVReport,
    LODGenerator,
    LODLevel,
    LODChain,
    CollisionGenerator,
    CollisionShape,
    CollisionType,
)

from .validation import GeometryValidator, GeometryValidationReport

from .assembly import ComponentizedCharacter, AssetBuildRecord

from .generators import (
    GeometryGenerator,
    GeometryGeneratorRegistry,
    ProceduralPrimitiveGenerator,
    ComponentizedHeroGenerator,
)

__all__ = [
    "MultiResLevel",
    "DetailRepresentation",
    "DetailPolicy",
    "Transform3D",
    "AABB",
    "BoundingSphere",
    "MeshData",
    "GeometryComponent",
    "ModifierType",
    "ProceduralModifier",
    "ModifierStack",
    "LandmarkSystem",
    "STANDARD_LANDMARKS",
    "AnatomyProfile",
    "AttachmentSocket",
    "ClothingLayerSystem",
    "LayerClearanceReport",
    "LAYER_HIERARCHY",
    "TopologyProcessor",
    "TopologyReport",
    "UVGenerator",
    "UVReport",
    "LODGenerator",
    "LODLevel",
    "LODChain",
    "CollisionGenerator",
    "CollisionShape",
    "CollisionType",
    "GeometryValidator",
    "GeometryValidationReport",
    "ComponentizedCharacter",
    "AssetBuildRecord",
    "GeometryGenerator",
    "GeometryGeneratorRegistry",
    "ProceduralPrimitiveGenerator",
    "ComponentizedHeroGenerator",
]
