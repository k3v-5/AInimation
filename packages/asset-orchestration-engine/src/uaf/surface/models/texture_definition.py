"""
TextureDefinition models physical or procedural texture artifacts.
UAF-81.4 Sections 21, 22, 24, 25.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .channels import ColorSpace, PBRChannel
from ...core.hashing.canonical_hasher import CanonicalHasher


class TextureSource(str, Enum):
    PROCEDURAL = "PROCEDURAL"
    BAKED = "BAKED"
    REFERENCE = "REFERENCE"
    GENERATED = "GENERATED"
    PAINTED = "PAINTED"
    PHOTOGRAPHIC = "PHOTOGRAPHIC"
    SCANNED = "SCANNED"
    DERIVED = "DERIVED"
    HYBRID = "HYBRID"


@dataclass
class TextureDefinition:
    texture_id: str
    channel: str  # PBRChannel value or custom
    resolution: int = 2048
    format: str = "PNG"  # PNG, TGA, EXR
    color_space: ColorSpace = ColorSpace.SRGB
    source: TextureSource = TextureSource.PROCEDURAL
    seed: int = 42
    generation_parameters: Dict[str, Any] = field(default_factory=dict)
    tiling: List[float] = field(default_factory=lambda: [1.0, 1.0])
    version: str = "1.0.0"

    @property
    def memory_bytes(self) -> int:
        # Standard uncompressed RGBA VRAM allocation
        return self.resolution * self.resolution * 4

    @property
    def texture_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())


    def to_dict(self) -> Dict[str, Any]:
        return {
            "texture_id": self.texture_id,
            "channel": self.channel,
            "resolution": self.resolution,
            "format": self.format,
            "color_space": self.color_space.value,
            "source": self.source.value,
            "seed": self.seed,
            "generation_parameters": self.generation_parameters,
            "tiling": self.tiling,
            "version": self.version,
        }
