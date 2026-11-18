"""Texture bridge for resolution, compression, and virtual texturing."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class TextureBridgePayload:
    asset_id: str
    semantic_name: str
    width: int
    height: int
    pixel_format: str = "BC7"
    is_srgb: bool = True
    is_normal_map: bool = False
    generate_mips: bool = True
    is_virtual_texture: bool = False
    compression_settings: str = "TC_Default"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "semantic_name": self.semantic_name,
            "width": self.width,
            "height": self.height,
            "pixel_format": self.pixel_format,
            "is_srgb": self.is_srgb,
            "is_normal_map": self.is_normal_map,
            "generate_mips": self.generate_mips,
            "is_virtual_texture": self.is_virtual_texture,
            "compression_settings": self.compression_settings,
            "metadata": self.metadata,
        }
