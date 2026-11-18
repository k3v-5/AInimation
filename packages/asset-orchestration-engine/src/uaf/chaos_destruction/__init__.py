"""
UAF-81.99: Physics, Voronoi Fracturing & Chaos Destruction System Package.
"""

from .core.contracts import (
    DestructionMaterialType,
    FracturePatternType,
    ClusterHierarchyLevel,
    AnchorMode,
    Vector3D,
    BoundingBox3D,
    VoronoiSite,
    FracturedPiece,
    AnchorFieldSpec,
    DebrisParticlePreset,
    GeometryCollectionSpec,
    ChaosDestructionBundle,
)
from .fracture.voronoi_engine import VoronoiFractureEngine
from .compiler.chaos_compiler import ChaosGeometryCollectionCompiler
from .debris.debris_emitter import DebrisFieldEmitter
from .export.ue5_chaos_exporter import UE5ChaosExporter

__all__ = [
    "DestructionMaterialType",
    "FracturePatternType",
    "ClusterHierarchyLevel",
    "AnchorMode",
    "Vector3D",
    "BoundingBox3D",
    "VoronoiSite",
    "FracturedPiece",
    "AnchorFieldSpec",
    "DebrisParticlePreset",
    "GeometryCollectionSpec",
    "ChaosDestructionBundle",
    "VoronoiFractureEngine",
    "ChaosGeometryCollectionCompiler",
    "DebrisFieldEmitter",
    "UE5ChaosExporter",
]
