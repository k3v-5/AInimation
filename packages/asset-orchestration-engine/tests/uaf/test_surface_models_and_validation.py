"""
Tests for Surface Models, Material Families, Instances, and Surface Validation.
UAF-81.4 Sections 4, 6, 7, 8, 14, 18, 19, 40, 71.
"""

from uaf.surface.models.channels import PBRChannel, ColorSpace, ShaderModel, ChannelPacking
from uaf.surface.models.texture_definition import TextureDefinition, TextureSource
from uaf.surface.models.material_layer import MaskType, MaskSource, BlendMode, SurfaceMask, MaterialLayer
from uaf.surface.models.material_definition import MaterialDefinition
from uaf.surface.models.material_instance import MaterialInstance
from uaf.surface.models.surface_definition import SemanticSurfaceRole, SurfaceDefinition
from uaf.surface.families.material_family import MaterialFamily
from uaf.surface.families.family_registry import MaterialFamilyRegistry
from uaf.surface.validation.surface_validator import SurfaceValidator


def test_texture_definition_and_hashing():
    tex = TextureDefinition(
        texture_id="T_Hero_BaseColor",
        channel=PBRChannel.BASE_COLOR.value,
        resolution=2048,
        color_space=ColorSpace.SRGB,
    )
    assert len(tex.texture_hash) == 64
    data = tex.to_dict()
    assert data["color_space"] == "sRGB"
    assert data["resolution"] == 2048


def test_material_family_creates_instance_with_overrides():
    family = MaterialFamily(
        family_id="CUSTOM_CHROME",
        name="Custom Chrome Master",
        base_shader_model=ShaderModel.DEFAULT_LIT,
        master_material_id="M_Master_Chrome",
        default_parameters={"metallic": 1.0, "roughness": 0.1, "tint": [1.0, 1.0, 1.0, 1.0]},
    )

    # Instantiate with roughness override
    instance = family.create_instance("MI_Chrome_Satin", parameter_overrides={"roughness": 0.35})
    assert instance.instance_id == "MI_Chrome_Satin"
    assert instance.parent_material_id == "M_Master_Chrome"
    assert instance.scalar_parameters["roughness"] == 0.35
    assert instance.scalar_parameters["metallic"] == 1.0
    assert instance.vector_parameters["tint"] == [1.0, 1.0, 1.0, 1.0]


def test_standard_material_family_registry():
    reg = MaterialFamilyRegistry()
    assert reg.supports("PAINTED_METAL")
    assert reg.supports("HUMAN_SKIN")
    assert reg.supports("TACTICAL_CLOTH")
    assert reg.supports("WEAPON_STEEL")
    assert reg.supports("EMISSIVE_GLASS")

    skin_family = reg.get("HUMAN_SKIN")
    assert skin_family.base_shader_model == ShaderModel.SUBSURFACE


def test_surface_validator_color_space_rules():
    # 1. BaseColor with linear color space must fail (Section 19)
    bad_base = TextureDefinition(
        texture_id="T_Bad_BC",
        channel="BASE_COLOR",
        resolution=2048,
        color_space=ColorSpace.LINEAR,  # Violation!
    )
    issues = SurfaceValidator.validate_texture(bad_base)
    assert any("must use sRGB color space" in iss for iss in issues)

    # 2. NormalMap with sRGB color space must fail
    bad_normal = TextureDefinition(
        texture_id="T_Bad_N",
        channel="NORMAL",
        resolution=2048,
        color_space=ColorSpace.SRGB,  # Violation!
    )
    issues_n = SurfaceValidator.validate_texture(bad_normal)
    assert any("must use NormalMap color space" in iss for iss in issues_n)

    # 3. Packed ORM with sRGB must fail
    bad_orm = TextureDefinition(
        texture_id="T_Bad_ORM",
        channel="ORM",
        resolution=2048,
        color_space=ColorSpace.SRGB,  # Violation!
    )
    issues_orm = SurfaceValidator.validate_texture(bad_orm)
    assert any("must use Linear color space" in iss for iss in issues_orm)


def test_surface_validator_power_of_two_and_vram_budget():
    non_pow2 = TextureDefinition(
        texture_id="T_NonPow2",
        channel="BASE_COLOR",
        resolution=1500,  # Violation!
        color_space=ColorSpace.SRGB,
    )
    issues = SurfaceValidator.validate_texture(non_pow2)
    assert any("not a valid power of 2" in iss for iss in issues)

    # VRAM budget test
    tex1 = TextureDefinition("T_1", "BASE_COLOR", resolution=4096, color_space=ColorSpace.SRGB)
    tex2 = TextureDefinition("T_2", "NORMAL", resolution=4096, color_space=ColorSpace.NORMAL_MAP)
    # 4096*4096*4 = 64 MB each -> 128 MB total
    rep = SurfaceValidator.validate_material_suite([tex1, tex2], max_vram_budget_mb=100.0)
    assert rep.is_valid is False
    assert any("exceeds maximum budget" in iss for iss in rep.issues)
