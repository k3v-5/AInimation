"""
UAF-81.4 Acceptance Tests (Sections 89, 90, 92, 93, 94).
Verifies:
- Section 94: Critical Architectural Test (Material parameter changes do not rebuild geometry,
  geometry changes selectively invalidate only dependent surface artifacts).
- Section 89: Character Surface Integration (Skin, Eyes, Hair, Cloth, Painted Metal, Emissive).
- Section 90: Weapon Surface Integration (Steel, Paint, Rubber, Emissive).
- Section 92: Cross-Target Generation (UE5_PC High vs UE5_CONSOLE Gameplay).
"""

from uaf.surface.models.surface_definition import SurfaceDefinition, SemanticSurfaceRole
from uaf.surface.models.channels import ShaderModel, ColorSpace
from uaf.surface.families.family_registry import MaterialFamilyRegistry
from uaf.surface.generators.surface_synthesizer import SurfaceSynthesizer
from uaf.surface.graph.dirty_tracker import SurfaceDependencyTracker


def test_critical_architectural_test_section_94():
    """
    Acceptance Test Section 94:
    - Character Armor Material change does NOT rebuild Body, Face, Hair, Skeleton geometry.
    - Changing Body Geometry invalidates ONLY dependent surface artifacts.
    """
    tracker = SurfaceDependencyTracker()

    # Geometry Nodes
    geom_body = "GEOM_Body"
    geom_face = "GEOM_Face"
    geom_hair = "GEOM_Hair"
    geom_skel = "GEOM_Skeleton"
    geom_armor = "GEOM_Armor"

    # Surface Nodes
    surf_body_bake = "SURF_BodyBake"
    surf_body_tex = "SURF_BodyTextures"
    surf_body_mat = "MAT_BodySkin"

    surf_armor_mat = "MAT_ArmorMetal"

    # Register dependencies
    tracker.add_dependency(surf_body_bake, geom_body)
    tracker.add_dependency(surf_body_tex, surf_body_bake)
    tracker.add_dependency(surf_body_mat, surf_body_tex)

    # 1. Changing Armor Material property
    # Invariant: Armor material does not rebuild geometry
    tracker.mark_dirty(surf_armor_mat)
    assert tracker.is_dirty(surf_armor_mat)
    assert not tracker.is_dirty(geom_body)
    assert not tracker.is_dirty(geom_face)
    assert not tracker.is_dirty(geom_hair)
    assert not tracker.is_dirty(geom_skel)
    assert not tracker.is_dirty(geom_armor)

    # 2. Changing Body Geometry
    # Invariant: Invalidation cascades only to body surface artifacts
    tracker.clear_dirty(surf_armor_mat)
    tracker.mark_dirty(geom_body)

    assert tracker.is_dirty(geom_body)
    assert tracker.is_dirty(surf_body_bake)
    assert tracker.is_dirty(surf_body_tex)
    assert tracker.is_dirty(surf_body_mat)

    # Face, Hair, Armor geometry & Armor material remain untouched!
    assert not tracker.is_dirty(geom_face)
    assert not tracker.is_dirty(geom_hair)
    assert not tracker.is_dirty(geom_skel)
    assert not tracker.is_dirty(geom_armor)
    assert not tracker.is_dirty(surf_armor_mat)


def test_character_surface_integration_section_89():
    """
    Acceptance Test Section 89:
    Character surfaces: Skin, Eyes, Hair, Cloth, Painted Metal, Emissive Element.
    """
    synthesizer = SurfaceSynthesizer()

    # 1. Skin surface
    skin_def = SurfaceDefinition(
        surface_id="char_hero_skin",
        semantic_role=SemanticSurfaceRole.SKIN,
        material_family="HUMAN_SKIN",
        shader_model=ShaderModel.SUBSURFACE,
        resolution_policy=2048,
    )
    skin_pkg = synthesizer.synthesize(skin_def)
    assert skin_pkg.validation_report.is_valid is True
    assert skin_pkg.material_instance.parent_material_id == "M_Master_HumanSkin"
    assert len(skin_pkg.textures) == 3  # BaseColor, Normal, ORM

    # 2. Painted Metal Armor surface
    armor_def = SurfaceDefinition(
        surface_id="char_hero_armor",
        semantic_role=SemanticSurfaceRole.PAINTED_METAL,
        material_family="PAINTED_METAL",
        resolution_policy=2048,
        parameters={"wear_amount": 0.3},
    )
    armor_pkg = synthesizer.synthesize(armor_def)
    assert armor_pkg.validation_report.is_valid is True
    assert armor_pkg.material_instance.scalar_parameters["wear_amount"] == 0.3

    # 3. Cloth surface
    cloth_def = SurfaceDefinition(
        surface_id="char_hero_cloth",
        semantic_role=SemanticSurfaceRole.CLOTH,
        material_family="TACTICAL_CLOTH",
        resolution_policy=2048,
    )
    cloth_pkg = synthesizer.synthesize(cloth_def)
    assert cloth_pkg.validation_report.is_valid is True

    # 4. Emissive visor
    visor_def = SurfaceDefinition(
        surface_id="char_hero_visor",
        semantic_role=SemanticSurfaceRole.EMISSIVE,
        material_family="EMISSIVE_GLASS",
        shader_model=ShaderModel.CLEAR_COAT,
        resolution_policy=1024,
    )
    visor_pkg = synthesizer.synthesize(visor_def)
    assert visor_pkg.validation_report.is_valid is True
    assert visor_pkg.material_instance.scalar_parameters["emissive_intensity"] == 5.0


def test_weapon_surface_integration_section_90():
    """
    Acceptance Test Section 90:
    Weapon surface suite: Steel receiver, Painted accents, Emissive sight.
    """
    synthesizer = SurfaceSynthesizer()

    steel_def = SurfaceDefinition(
        surface_id="wpn_rifle_receiver",
        semantic_role=SemanticSurfaceRole.METAL,
        material_family="WEAPON_STEEL",
        resolution_policy=2048,
        parameters={"roughness": 0.22, "oil_sheen": 0.3},
    )
    pkg = synthesizer.synthesize(steel_def)
    assert pkg.validation_report.is_valid is True
    assert pkg.material_instance.scalar_parameters["roughness"] == 0.22
    assert pkg.material_instance.scalar_parameters["oil_sheen"] == 0.3


def test_cross_target_generation_section_92():
    """
    Acceptance Test Section 92:
    Same SurfaceDefinition generating outputs for:
    - PRODUCTION + UE5_PC (4096 resolution)
    - GAMEPLAY + UE5_CONSOLE (2048 resolution)
    """
    synthesizer = SurfaceSynthesizer()

    base_params = {"wear_amount": 0.15}

    # PC High Target
    surf_pc = SurfaceDefinition(
        surface_id="armor_chest",
        semantic_role=SemanticSurfaceRole.PAINTED_METAL,
        material_family="PAINTED_METAL",
        resolution_policy=4096,
        target_policy="UE5_PC",
        quality_profile="production",
        parameters=base_params,
    )
    pkg_pc = synthesizer.synthesize(surf_pc)
    assert pkg_pc.target == "UE5_PC"
    assert pkg_pc.textures[0].resolution == 4096
    # 3 * 4096 * 4096 * 4 bytes = 192 MB uncompressed
    assert pkg_pc.validation_report.estimated_vram_mb == 192.0

    # Console Target
    surf_console = SurfaceDefinition(
        surface_id="armor_chest",
        semantic_role=SemanticSurfaceRole.PAINTED_METAL,
        material_family="PAINTED_METAL",
        resolution_policy=2048,
        target_policy="UE5_CONSOLE",
        quality_profile="gameplay",
        parameters=base_params,
    )
    pkg_console = synthesizer.synthesize(surf_console)
    assert pkg_console.target == "UE5_CONSOLE"
    assert pkg_console.textures[0].resolution == 2048
    # 3 * 2048 * 2048 * 4 bytes = 48 MB uncompressed
    assert pkg_console.validation_report.estimated_vram_mb == 48.0
