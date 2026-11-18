"""
SurfaceSynthesizer transforms a SurfaceDefinition into textures, packed maps, and Unreal Engine-ready materials.
UAF-81.4 Sections 1, 23, 27, 40, 83.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.surface_definition import SurfaceDefinition, SemanticSurfaceRole
from ..models.texture_definition import TextureDefinition, TextureSource
from ..models.channels import PBRChannel, ColorSpace, ChannelPacking
from ..models.material_instance import MaterialInstance
from ..families.family_registry import MaterialFamilyRegistry
from ..validation.surface_validator import SurfaceValidator, SurfaceValidationReport


@dataclass
class UnrealSurfacePackage:
    surface_id: str
    target: str
    material_instance: MaterialInstance
    textures: List[TextureDefinition]
    channel_packing: Optional[ChannelPacking]
    validation_report: SurfaceValidationReport

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "target": self.target,
            "material_instance": self.material_instance.to_dict(),
            "textures": [t.to_dict() for t in self.textures],
            "channel_packing": self.channel_packing.to_dict() if self.channel_packing else None,
            "validation_report": self.validation_report.to_dict(),
        }


class SurfaceSynthesizer:
    """
    High-level orchestrator transforming surface specifications into production-ready texture and material suites.
    """
    def __init__(self, family_registry: Optional[MaterialFamilyRegistry] = None):
        self.family_registry = family_registry or MaterialFamilyRegistry()

    def synthesize(self, surface_def: SurfaceDefinition, seed: int = 42) -> UnrealSurfacePackage:
        family = self.family_registry.get(surface_def.material_family)
        if not family:
            raise ValueError(f"Unknown material family '{surface_def.material_family}'.")

        res = surface_def.resolution_policy
        generated_textures: List[TextureDefinition] = []

        # 1. Generate BaseColor texture
        tex_base = TextureDefinition(
            texture_id=f"T_{surface_def.surface_id}_BC",
            channel=PBRChannel.BASE_COLOR.value,
            resolution=res,
            color_space=ColorSpace.SRGB,
            source=TextureSource.PROCEDURAL,
            seed=seed,
            generation_parameters={"semantic_role": surface_def.semantic_role.value},
        )
        generated_textures.append(tex_base)

        # 2. Generate Normal texture
        tex_normal = TextureDefinition(
            texture_id=f"T_{surface_def.surface_id}_N",
            channel=PBRChannel.NORMAL.value,
            resolution=res,
            color_space=ColorSpace.NORMAL_MAP,
            source=TextureSource.PROCEDURAL,
            seed=seed + 1,
        )
        generated_textures.append(tex_normal)

        # 3. Generate Packed ORM texture (Occlusion, Roughness, Metallic)
        packing = ChannelPacking(
            packed_texture_id=f"T_{surface_def.surface_id}_ORM",
            r_channel=PBRChannel.AMBIENT_OCCLUSION.value,
            g_channel=PBRChannel.ROUGHNESS.value,
            b_channel=PBRChannel.METALLIC.value,
            color_space=ColorSpace.LINEAR,
        )
        tex_orm = TextureDefinition(
            texture_id=packing.packed_texture_id,
            channel="ORM",
            resolution=res,
            color_space=ColorSpace.LINEAR,
            source=TextureSource.PROCEDURAL,
            seed=seed + 2,
        )
        generated_textures.append(tex_orm)

        # 4. Create Material Instance
        tex_params = {
            "BaseColorTexture": tex_base.texture_id,
            "NormalTexture": tex_normal.texture_id,
            "ORMTexture": tex_orm.texture_id,
        }
        instance_overrides = dict(surface_def.parameters)
        instance_overrides.update(tex_params)

        mat_instance = family.create_instance(
            instance_id=f"MI_{surface_def.surface_id}",
            parameter_overrides=instance_overrides,
        )

        # 5. Validation
        val_rep = SurfaceValidator.validate_material_suite(generated_textures)

        return UnrealSurfacePackage(
            surface_id=surface_def.surface_id,
            target=surface_def.target_policy,
            material_instance=mat_instance,
            textures=generated_textures,
            channel_packing=packing,
            validation_report=val_rep,
        )
