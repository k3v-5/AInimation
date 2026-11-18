"""
TextureAtlasDefinition and UDIMDefinition for multi-tile and packed asset texturing.
UAF-81.7 Sections 24, 25.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional


@dataclass
class TextureAtlasDefinition:
    atlas_id: str
    resolution: int = 4096
    sub_textures: Dict[str, List[float]] = field(default_factory=dict)  # asset_id -> [u_min, v_min, u_max, v_max]

    def add_sub_texture(self, asset_id: str, rect: List[float]) -> None:
        self.sub_textures[asset_id] = rect

    def get_uv_rect(self, asset_id: str) -> Optional[List[float]]:
        return self.sub_textures.get(asset_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "atlas_id": self.atlas_id,
            "resolution": self.resolution,
            "sub_textures": self.sub_textures,
        }


@dataclass
class UDIMDefinition:
    tile_ids: List[int] = field(default_factory=lambda: [1001])
    tile_resolutions: Dict[int, int] = field(default_factory=lambda: {1001: 4096})

    def add_tile(self, tile_id: int, resolution: int = 4096) -> None:
        if tile_id not in self.tile_ids:
            self.tile_ids.append(tile_id)
        self.tile_resolutions[tile_id] = resolution

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tile_ids": self.tile_ids,
            "tile_resolutions": self.tile_resolutions,
        }
