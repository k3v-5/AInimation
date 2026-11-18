"""
MaterialFamily defines shared shader logic, parameter standards, and layers for related surfaces.
UAF-81.4 Sections 6, 45, 46.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.channels import ShaderModel
from ..models.material_instance import MaterialInstance


@dataclass
class MaterialFamily:
    family_id: str
    name: str
    base_shader_model: ShaderModel
    master_material_id: str
    supported_layers: List[str] = field(default_factory=list)
    default_parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def create_instance(
        self,
        instance_id: str,
        parameter_overrides: Optional[Dict[str, Any]] = None,
    ) -> MaterialInstance:
        """
        Creates a lightweight material instance inheriting family parameters.
        UAF-81.4 Section 40, 46.
        """
        scalars: Dict[str, float] = {}
        vectors: Dict[str, List[float]] = {}
        textures: Dict[str, str] = {}
        switches: Dict[str, bool] = {}

        # Merge defaults
        combined_params = dict(self.default_parameters)
        if parameter_overrides:
            combined_params.update(parameter_overrides)

        for k, v in combined_params.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                scalars[k] = float(v)
            elif isinstance(v, list):
                vectors[k] = [float(x) for x in v]
            elif isinstance(v, str):
                textures[k] = v
            elif isinstance(v, bool):
                switches[k] = v

        return MaterialInstance(
            instance_id=instance_id,
            parent_material_id=self.master_material_id,
            scalar_parameters=scalars,
            vector_parameters=vectors,
            texture_parameters=textures,
            static_switch_parameters=switches,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "family_id": self.family_id,
            "name": self.name,
            "base_shader_model": self.base_shader_model.value,
            "master_material_id": self.master_material_id,
            "supported_layers": self.supported_layers,
            "default_parameters": self.default_parameters,
            "description": self.description,
        }
