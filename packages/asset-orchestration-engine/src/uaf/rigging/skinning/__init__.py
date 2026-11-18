"""
UAF Rigging Skinning Package
"""

from .skinning_definition import WeightMethod, VertexWeights, SkinningDefinition
from .weight_normalizer import WeightNormalizer
from .weight_generator import WeightGenerator

__all__ = [
    "WeightMethod",
    "VertexWeights",
    "SkinningDefinition",
    "WeightNormalizer",
    "WeightGenerator",
]
