"""
TextureSet aggregates all PBR textures, packed maps, and masks for a surface.
UAF-81.7 Section 10.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .texture_definition import TextureDefinition
from .channels import PBRChannel
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class TextureSet:
    set_id: str
    textures: Dict[str, TextureDefinition] = field(default_factory=dict)
    resolution: int = 2048
    is_orm_packed: bool = True
    version: str = "1.0.0"

    def add_texture(self, channel: str, texture: TextureDefinition) -> None:
        self.textures[channel] = texture

    def get_texture(self, channel: str) -> Optional[TextureDefinition]:
        return self.textures.get(channel)

    @property
    def total_memory_bytes(self) -> int:
        return sum(t.memory_bytes for t in self.textures.values())

    @property
    def set_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "set_id": self.set_id,
            "resolution": self.resolution,
            "is_orm_packed": self.is_orm_packed,
            "textures": {k: v.to_dict() for k, v in sorted(self.textures.items())},
            "total_memory_bytes": self.total_memory_bytes,
            "version": self.version,
        }
