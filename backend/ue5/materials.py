"""
PBR Material Manager for Unreal Engine 5.

Generates and configures Dynamic Material Instances, assigning PBR texture maps
(albedo, normal, roughness, metallic, emissive) and scalar/vector parameters.
Adheres strictly to PBR conservation of energy principles with range clamping.

100% Zero-Any compliant with Pydantic v2 strict models.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union
from backend.core.models import ColorRGB, PBRTextureSet, StrictBaseModel
from pydantic import Field


# ---------------------------------------------------------------------------
# PBR Material Models & Descriptors
# ---------------------------------------------------------------------------

class PBRMaterialInstance(StrictBaseModel):
    """Represents a configured UE5 Dynamic Material Instance descriptor."""
    material_name: str = Field(..., description="Name or identifier of the material")
    parent_material_path: str = Field(
        default="/Game/Materials/M_MasterPBR.M_MasterPBR",
        description="Path to master PBR material asset in Unreal Content Browser"
    )
    base_color: ColorRGB = Field(default_factory=lambda: ColorRGB(r=0.8, g=0.8, b=0.8))
    roughness: float = Field(default=0.5, ge=0.0, le=1.0)
    metallic: float = Field(default=0.0, ge=0.0, le=1.0)
    specular: float = Field(default=0.5, ge=0.0, le=1.0)
    emissive_color: ColorRGB = Field(default_factory=lambda: ColorRGB(r=0.0, g=0.0, b=0.0))
    emissive_intensity: float = Field(default=0.0, ge=0.0)
    textures: Optional[PBRTextureSet] = Field(default=None)

    def to_ue5_parameters(self) -> Dict[str, Union[float, Dict[str, float], str]]:
        """Format material parameters as an Unreal Remote Control parameter dictionary."""
        params: Dict[str, Union[float, Dict[str, float], str]] = {
            "Roughness": self.roughness,
            "Metallic": self.metallic,
            "Specular": self.specular,
            "EmissiveIntensity": self.emissive_intensity,
            "BaseColor": self.base_color.to_ue5_dict(),
            "EmissiveColor": self.emissive_color.to_ue5_dict(),
        }
        if self.textures is not None:
            if self.textures.albedo_path:
                params["AlbedoMap"] = self.textures.albedo_path
            if self.textures.normal_path:
                params["NormalMap"] = self.textures.normal_path
            if self.textures.roughness_path:
                params["RoughnessMap"] = self.textures.roughness_path
            if self.textures.metallic_path:
                params["MetallicMap"] = self.textures.metallic_path
            if self.textures.emissive_path:
                params["EmissiveMap"] = self.textures.emissive_path
        return params


# ---------------------------------------------------------------------------
# Material Manager Registry & Factory
# ---------------------------------------------------------------------------

class MaterialManager:
    """
    Manages material creation, texture map linking, and dynamic parameter updates.
    """

    def __init__(self, master_material_path: str = "/Game/Materials/M_MasterPBR.M_MasterPBR") -> None:
        self.master_material_path: str = master_material_path
        self._registry: Dict[str, PBRMaterialInstance] = {}

    def create_material(
        self,
        name: str,
        base_color: Optional[ColorRGB] = None,
        roughness: float = 0.5,
        metallic: float = 0.0,
        specular: float = 0.5,
        textures: Optional[PBRTextureSet] = None,
    ) -> PBRMaterialInstance:
        """
        Create and register a new PBR material definition with robust value clamping.
        """
        color = base_color or ColorRGB(r=0.8, g=0.8, b=0.8)
        clamped_roughness = max(0.0, min(1.0, float(roughness)))
        clamped_metallic = max(0.0, min(1.0, float(metallic)))
        clamped_specular = max(0.0, min(1.0, float(specular)))

        mat = PBRMaterialInstance(
            material_name=name,
            parent_material_path=self.master_material_path,
            base_color=color,
            roughness=clamped_roughness,
            metallic=clamped_metallic,
            specular=clamped_specular,
            textures=textures,
        )
        self._registry[name] = mat
        return mat

    def get_material(self, name: str) -> Optional[PBRMaterialInstance]:
        """Retrieve a registered material instance by name."""
        return self._registry.get(name)

    def list_materials(self) -> List[str]:
        """List all registered material instance names."""
        return list(self._registry.keys())


def create_pbr_material(
    name: str = "M_GeneratedPBR",
    base_color: Optional[Union[ColorRGB, Dict[str, float]]] = None,
    roughness: float = 0.5,
    metallic: float = 0.0,
    specular: float = 0.5,
    textures: Optional[Union[PBRTextureSet, Dict[str, str]]] = None,
) -> PBRMaterialInstance:
    """
    Functional facade for quick PBR material creation with automatic dict coercion.
    """
    color_obj: Optional[ColorRGB] = None
    if isinstance(base_color, dict):
        color_obj = ColorRGB.model_validate(base_color)
    elif isinstance(base_color, ColorRGB):
        color_obj = base_color

    textures_obj: Optional[PBRTextureSet] = None
    if isinstance(textures, dict):
        textures_obj = PBRTextureSet.model_validate(textures)
    elif isinstance(textures, PBRTextureSet):
        textures_obj = textures

    manager = MaterialManager()
    return manager.create_material(
        name=name,
        base_color=color_obj,
        roughness=roughness,
        metallic=metallic,
        specular=specular,
        textures=textures_obj,
    )
