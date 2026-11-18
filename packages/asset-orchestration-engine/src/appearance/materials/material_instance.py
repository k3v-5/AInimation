from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .material_schema import MaterialDefinition, PBRParameters

@dataclass
class MaterialInstance:
    instance_id: str
    base_material_id: str
    component_id: str
    parameter_overrides: Dict[str, Any] = field(default_factory=dict)
    texture_overrides: Dict[str, str] = field(default_factory=dict)
    version: int = 1

    def get_effective_parameters(self, base_mat: MaterialDefinition) -> Dict[str, Any]:
        """
        Combina los parámetros base con las sobreescrituras locales.
        """
        effective = {
            "base_color": base_mat.parameters.base_color,
            "metallic": base_mat.parameters.metallic,
            "roughness": base_mat.parameters.roughness,
            "specular": base_mat.parameters.specular,
            "normal_strength": base_mat.parameters.normal_strength,
            "emission_color": base_mat.parameters.emission_color,
            "emission_strength": base_mat.parameters.emission_strength,
            "alpha": base_mat.parameters.alpha
        }
        effective.update(self.parameter_overrides)
        return effective
