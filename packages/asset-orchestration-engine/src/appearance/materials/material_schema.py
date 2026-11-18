from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple

class ShaderType(str, Enum):
    PBR = "PBR"
    UNLIT = "UNLIT"
    EMISSIVE = "EMISSIVE"

@dataclass
class PBRParameters:
    base_color: str = "#CCCCCC"
    metallic: float = 0.0
    roughness: float = 0.5
    specular: float = 0.5
    normal_strength: float = 1.0
    emission_color: str = "#000000"
    emission_strength: float = 0.0
    alpha: float = 1.0

    def validate(self) -> Tuple[bool, Optional[str]]:
        if not (0.0 <= self.metallic <= 1.0):
            return False, f"INVALID_MATERIAL_PARAMETER: metallic must be in range [0, 1], got {self.metallic}."
        if not (0.0 <= self.roughness <= 1.0):
            return False, f"INVALID_MATERIAL_PARAMETER: roughness must be in range [0, 1], got {self.roughness}."
        if not (0.0 <= self.specular <= 1.0):
            return False, f"INVALID_MATERIAL_PARAMETER: specular must be in range [0, 1], got {self.specular}."
        if self.normal_strength < 0.0:
            return False, f"INVALID_MATERIAL_PARAMETER: normal_strength must be >= 0, got {self.normal_strength}."
        if not (0.0 <= self.alpha <= 1.0):
            return False, f"INVALID_MATERIAL_PARAMETER: alpha must be in range [0, 1], got {self.alpha}."
        return True, None

@dataclass
class MaterialDefinition:
    material_id: str
    name: str
    shader_type: ShaderType = ShaderType.PBR
    parameters: PBRParameters = field(default_factory=PBRParameters)
    textures: Dict[str, str] = field(default_factory=dict) # usage -> texture_id
    version: int = 1
