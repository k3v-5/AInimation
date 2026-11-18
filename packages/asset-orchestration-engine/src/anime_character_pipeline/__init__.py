"""
Anime Character Pipeline Module
===============================
Provides organic topology generation, bezier hair systems, NPR cel-shading,
and inverted hull outline techniques for authentic anime 3D characters.
"""

from .api.anime_character_api import AnimeCharacterAPI
from .core.anime_types import (
    AnimeProportionsPreset,
    AnimeEyeStyle,
    AnimeHairStyle,
    NPROutlineMode,
    AnimeShadingModel
)
from .core.anime_schema import (
    AnimeCharacterSpec,
    AnimeHairStrandSpec,
    AnimeHeadTopologySpec,
    AnimeBodyTopologySpec,
    NPROutlineSpec,
    AnimeCharacterBuildResult
)

__all__ = [
    "AnimeCharacterAPI",
    "AnimeProportionsPreset",
    "AnimeEyeStyle",
    "AnimeHairStyle",
    "NPROutlineMode",
    "AnimeShadingModel",
    "AnimeCharacterSpec",
    "AnimeHairStrandSpec",
    "AnimeHeadTopologySpec",
    "AnimeBodyTopologySpec",
    "NPROutlineSpec",
    "AnimeCharacterBuildResult",
]
