"""
Anime Types and Enumerations
============================
Agnostic domain types for authentic anime 3D character generation.
"""

from enum import Enum


class AnimeProportionsPreset(str, Enum):
    """Canon anime proportions presets."""
    STANDARD_SHONEN_FEMALE = "standard_shonen_female"   # 1:7.0 - 1:7.2 heads, stylized athletic
    CYBER_OPERATIVE = "cyber_operative"                 # 1:7.2 heads, 1.68m, long legs
    CHIBI_SD = "chibi_sd"                               # 1:3.0 - 1:4.0 heads, super-deformed
    SEINEN_ACTION = "seinen_action"                     # 1:7.5 - 1:7.8 heads, mature combat


class AnimeEyeStyle(str, Enum):
    """Stylized anime eye shape presets."""
    OVAL_LARGE = "oval_large"           # Classic large anime aperture
    CAT_EYE_ALMOND = "cat_eye_almond"   # Sharp, cool anime operative look
    ROUND_HEROIC = "round_heroic"       # Expressive open heroic look


class AnimeHairStyle(str, Enum):
    """Anime hair architecture presets using bezier curve systems."""
    HIGH_PONYTAIL_LAYERED = "high_ponytail_layered"  # High ponytail + bangs + sideburns
    TWIN_TAILS = "twin_tails"                        # Classic anime twin tails
    BOB_CUT_STYLIZED = "bob_cut_stylized"            # Short layered combat bob
    LONG_FLOWING = "long_flowing"                    # Long flowing strands


class NPROutlineMode(str, Enum):
    """Non-Photorealistic Rendering outline generation strategies."""
    INVERTED_HULL_SOLIDIFY = "inverted_hull_solidify"  # Arc System Works / Guilty Gear standard
    FREESTYLE_POST = "freestyle_post"                  # Line art post-process
    NONE = "none"


class AnimeShadingModel(str, Enum):
    """Cel-shading illumination model."""
    TWO_TONE_BANDED = "two_tone_banded"        # Crisp hard shadow boundary (Guilty Gear style)
    THREE_TONE_SMOOTH = "three_tone_smooth"    # Softened midtone + core shadow (Genshin style)
    HYBRID_PBR_TOON = "hybrid_pbr_toon"        # Cel-shaded base with subtle PBR metallicity
