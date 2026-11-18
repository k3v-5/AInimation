"""
ProceduralTextureSynthesizer generates deterministic procedural PBR texture sets and surface masks.
UAF-81.7 Sections 26, 27, 28, 29, 30, 31, 32, 78.
"""

import math
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.texture_definition import TextureDefinition, TextureSource
from ..models.texture_set import TextureSet
from ..models.channels import PBRChannel, ColorSpace
from ...core.hashing.canonical_hasher import CanonicalHasher


class ProceduralPatternType(str, Enum):
    NOISE = "NOISE"
    VORONOI = "VORONOI"
    CELLULAR = "CELLULAR"
    WEAR_DIRT = "WEAR_DIRT"
    SCRATCHES = "SCRATCHES"
    RUST = "RUST"
    EMISSIVE_GRID = "EMISSIVE_GRID"


class ProceduralTextureSynthesizer:
    """
    Generates deterministic mathematical patterns, wear patterns, and complete PBR texture sets.
    """
    @classmethod
    def generate_pattern_texture(
        cls,
        texture_id: str,
        pattern_type: ProceduralPatternType,
        resolution: int = 2048,
        seed: int = 42,
        color_space: ColorSpace = ColorSpace.LINEAR,
    ) -> TextureDefinition:
        raw_metadata = {
            "texture_id": texture_id,
            "pattern_type": pattern_type.value,
            "resolution": resolution,
            "seed": seed,
            "color_space": color_space.value,
        }
        tex_hash = CanonicalHasher.compute_hash(raw_metadata)

        return TextureDefinition(
            texture_id=texture_id,
            resolution=resolution,
            color_space=color_space,
            channel=PBRChannel.ROUGHNESS.value if color_space == ColorSpace.LINEAR else PBRChannel.BASE_COLOR.value,
            source=TextureSource.PROCEDURAL,
            generation_parameters=raw_metadata,
        )

    @classmethod
    def synthesize_pbr_set(
        cls,
        set_id: str,
        material_family: str = "PAINTED_METAL",
        resolution: int = 2048,
        seed: int = 42,
    ) -> TextureSet:
        """
        Synthesizes a complete, calibrated PBR TextureSet according to the physical material family.
        """
        tex_set = TextureSet(set_id=set_id, resolution=resolution, is_orm_packed=True)

        # 1. BaseColor (sRGB)
        base_color = TextureDefinition(
            texture_id=f"T_{set_id}_BaseColor",
            resolution=resolution,
            color_space=ColorSpace.SRGB,
            channel=PBRChannel.BASE_COLOR.value,
            source=TextureSource.PROCEDURAL,
            generation_parameters={"family": material_family, "type": "albedo"},
        )
        tex_set.add_texture(PBRChannel.BASE_COLOR.value, base_color)

        # 2. Normal (NormalMap)
        normal = TextureDefinition(
            texture_id=f"T_{set_id}_Normal",
            resolution=resolution,
            color_space=ColorSpace.NORMAL_MAP,
            channel=PBRChannel.NORMAL.value,
            source=TextureSource.BAKED,
            generation_parameters={"family": material_family, "type": "tangent_normal"},
        )
        tex_set.add_texture(PBRChannel.NORMAL.value, normal)

        # 3. Packed ORM (Linear)
        orm = TextureDefinition(
            texture_id=f"T_{set_id}_ORM",
            resolution=resolution,
            color_space=ColorSpace.LINEAR,
            channel=PBRChannel.METALLIC.value,  # packed container
            source=TextureSource.PROCEDURAL,
            generation_parameters={"family": material_family, "packed": "R=AO,G=Roughness,B=Metallic"},
        )
        tex_set.add_texture("ORM", orm)

        # 4. Optional Emissive (if EMISSIVE family)
        if "EMISSIVE" in material_family.upper():
            emissive = TextureDefinition(
                texture_id=f"T_{set_id}_Emissive",
                resolution=resolution,
                color_space=ColorSpace.LINEAR,
                channel=PBRChannel.EMISSIVE.value,
                source=TextureSource.PROCEDURAL,
                generation_parameters={"family": material_family, "emissive_multiplier": 5.0},
            )
            tex_set.add_texture(PBRChannel.EMISSIVE.value, emissive)

        return tex_set

