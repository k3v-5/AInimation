"""
UAF-81.84.5: Material Parameter Bindings and Shader Dynamic Uniforms.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

from ..emitter.particle import Particle
from ..models.definition import VFXMaterialBinding


class MaterialBindingManager:
    """Binds particle simulation attributes to material shader parameters."""

    def __init__(self, binding: VFXMaterialBinding | None = None):
        self.binding = binding or VFXMaterialBinding(
            material_id="default_vfx_mat",
            parameter_mappings={
                "ParticleColor": "color",
                "ParticleSize": "size",
                "ParticleAge": "normalized_age",
            },
        )

    def extract_uniforms(self, particle: Particle) -> Dict[str, Any]:
        """Extract material uniform dictionary from particle attributes according to mappings."""
        uniforms = {}
        for shader_param, attr_name in self.binding.parameter_mappings.items():
            if attr_name == "normalized_age":
                uniforms[shader_param] = particle.normalized_age
            elif attr_name in particle.attributes:
                uniforms[shader_param] = particle.attributes[attr_name]
        return uniforms
