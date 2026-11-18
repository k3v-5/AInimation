from typing import Dict, Optional, List
from .texture_schema import TextureMetadata

class TextureRegistry:
    def __init__(self):
        self.textures: Dict[str, TextureMetadata] = {}

    def register_texture(self, texture: TextureMetadata):
        self.textures[texture.texture_id] = texture

    def get_texture(self, texture_id: str) -> Optional[TextureMetadata]:
        return self.textures.get(texture_id)

    def list_textures(self) -> List[TextureMetadata]:
        return list(self.textures.values())
