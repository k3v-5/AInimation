from typing import Dict, Any, Optional, List
from ..core.appearance_engine import AppearanceEngine
from ..materials.material_schema import ShaderType
from ..textures.texture_schema import TextureMetadata, TextureUsage, ColorSpace
from ..uv.uv_schema import UVMethod

class AppearanceAPI:
    def __init__(self, appearance_engine: AppearanceEngine):
        self.engine = appearance_engine

    def create_material(self, material_id: str, name: str, shader_type: str = "PBR", parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.engine.create_material(material_id, name, shader_type, parameters)

    def assign_material(self, component_id: str, material_id: str, slot_name: str = "default_slot") -> Dict[str, Any]:
        return self.engine.assign_material(component_id, material_id, slot_name)

    def modify_material(self, target_id: str, changes: Dict[str, Any], scope: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.modify_material(target_id, changes, scope, dry_run)

    def register_texture(self, texture_id: str, source_path: str, usage: str, color_space: str) -> Dict[str, Any]:
        tex = TextureMetadata(
            texture_id=texture_id,
            source_path=source_path,
            usage=TextureUsage(usage.upper()),
            color_space=ColorSpace(color_space)
        )
        return self.engine.register_texture(tex)

    def generate_uv(self, component_id: str, method: str = "BOX", channel: str = "UV0") -> Dict[str, Any]:
        return self.engine.generate_uv(component_id, UVMethod(method.upper()), channel)

    def get_manifest(self, asset_id: str) -> Dict[str, Any]:
        return self.engine.get_appearance_manifest(asset_id)

    def validate(self) -> Dict[str, Any]:
        return self.engine.validate_appearance()
