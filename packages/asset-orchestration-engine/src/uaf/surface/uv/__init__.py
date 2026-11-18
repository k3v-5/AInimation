"""
UAF Surface UV Package
"""

from .uv_definition import UVChannel, UVStrategy, UVOverlapPolicy, UVDefinition
from .trim_sheet import TrimRegion, TrimSheetDefinition
from .texture_atlas import TextureAtlasDefinition, UDIMDefinition

__all__ = [
    "UVChannel",
    "UVStrategy",
    "UVOverlapPolicy",
    "UVDefinition",
    "TrimRegion",
    "TrimSheetDefinition",
    "TextureAtlasDefinition",
    "UDIMDefinition",
]
