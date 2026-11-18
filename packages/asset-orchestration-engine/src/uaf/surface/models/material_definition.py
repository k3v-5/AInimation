"""
MaterialDefinition represents the master shader specification and parameter bindings.
UAF-81.4 Section 7.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .channels import ShaderModel
from .material_layer import MaterialLayer
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class MaterialDefinition:
    material_id: str
    material_name: str
    family_id: str
    shader_model: ShaderModel = ShaderModel.DEFAULT_LIT
    parameters: Dict[str, Any] = field(default_factory=dict)
    texture_bindings: Dict[str, str] = field(default_factory=dict)  # slot_name -> texture_id
    layer_stack: List[MaterialLayer] = field(default_factory=list)
    render_settings: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    @property
    def material_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_id": self.material_id,
            "material_name": self.material_name,
            "family_id": self.family_id,
            "shader_model": self.shader_model.value,
            "parameters": self.parameters,
            "texture_bindings": self.texture_bindings,
            "layer_stack": [l.to_dict() for l in sorted(self.layer_stack, key=lambda x: x.priority)],
            "render_settings": self.render_settings,
            "version": self.version,
        }
