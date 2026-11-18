"""
UAF-81.3 Acceptance Tests (Sections 69, 73, 75, 100, 101, 102).
Verifies:
- Section 101: Critical Integration Test (Componentized Character with Body != Face != Hair != Clothing != Armor
  and partial rebuild capability without monolithic remesh).
- Section 102: Critical Remesh Test (ProceduralPrimitiveGenerator for simple robots vs ComponentizedHeroGenerator
  for hero characters).
- Section 73: AssetBuildRecord and reproducible build tracking.
"""

from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.identity.asset_types import AssetType
from uaf.core.specification.asset_specification import AssetSpecification
from uaf.geometry.generators.procedural_primitive_generator import ProceduralPrimitiveGenerator
from uaf.geometry.generators.componentized_hero_generator import ComponentizedHeroGenerator
from uaf.geometry.models.mesh_data import MeshData
from uaf.geometry.assembly.build_record import AssetBuildRecord
from uaf.geometry.validation.geometry_validator import GeometryValidator


def test_critical_integration_section_101_componentized_character_and_partial_rebuild():
    """
    Acceptance Test Section 101:
    Demonstrates construction of a character containing Body, Head, Face, Eyes, Teeth, Hair,
    Clothing, Armor, Weapon, Accessories as independent components (Body != Face != Hair != Clothing != Armor),
    and proves partial rebuild without regenerating unrelated components.
    """
    spec = AssetSpecification(
        identity=AssetIdentity(asset_id="hero_warrior", asset_type=AssetType.CHARACTER),
        parameters={"height": 1.85},
    )

    generator = ComponentizedHeroGenerator()
    character = generator.generate_character_assembly(spec)

    # 1. Verify discrete independent components exist
    body = character.get_component("comp_body")
    head = character.get_component("comp_head")
    face = character.get_component("comp_face")
    eyes = character.get_component("comp_eyes")
    teeth = character.get_component("comp_teeth")
    hair = character.get_component("comp_hair")
    clothing = character.get_component("comp_clothing")
    armor = character.get_component("comp_armor")
    weapon = character.get_component("comp_weapon")

    assert body is not None
    assert head is not None
    assert face is not None
    assert eyes is not None
    assert teeth is not None
    assert hair is not None
    assert clothing is not None
    assert armor is not None
    assert weapon is not None

    # Verify they are separate components and have distinct material slots
    assert body is not face
    assert clothing is not armor
    assert body.material_slots != armor.material_slots

    initial_body_mesh = body.mesh_data
    initial_armor_mesh = armor.mesh_data

    # 2. Perform PARTIAL REBUILD on face component only (Section 75, 101)
    new_face_mesh = MeshData.create_cube(size=0.15)
    updated = character.update_component("comp_face", new_face_mesh)
    assert updated is True

    # Confirm face was updated
    assert character.get_component("comp_face").mesh_data is new_face_mesh
    # Confirm body and armor remain untouched and identical!
    assert character.get_component("comp_body").mesh_data is initial_body_mesh
    assert character.get_component("comp_armor").mesh_data is initial_armor_mesh


def test_critical_remesh_section_102_simple_robot_vs_hero_character():
    """
    Acceptance Test Section 102:
    - simple_robot uses procedural primitive geometry.
    - hero_character uses componentized geometry with specialized face, clothing, and UVs.
    """
    # 1. Simple Robot
    robot_spec = AssetSpecification(
        identity=AssetIdentity(asset_id="simple_patrol_robot", asset_type=AssetType.CHARACTER),
        parameters={"size": 1.2, "enable_remesh": True},
    )
    robot_gen = ProceduralPrimitiveGenerator()
    robot_root = robot_gen.generate(robot_spec)

    assert robot_root.semantic_role == "STRUCTURAL"
    assert robot_root.mesh_data is not None
    assert len(robot_root.children) == 1  # Attached sensor
    assert robot_root.total_triangle_count == 24  # Simple primitives

    # 2. Hero Character
    hero_spec = AssetSpecification(
        identity=AssetIdentity(asset_id="specialist_commander", asset_type=AssetType.CHARACTER),
        parameters={"height": 1.90},
    )
    hero_gen = ComponentizedHeroGenerator()
    hero_character = hero_gen.generate_character_assembly(hero_spec)

    # Must contain specialized multi-component hierarchy
    assert hero_character.get_component("comp_face") is not None
    assert hero_character.get_component("comp_clothing") is not None
    assert hero_character.get_component("comp_armor") is not None
    # Higher complexity than primitive robot
    assert hero_character.total_triangle_count > robot_root.total_triangle_count


def test_asset_build_record_provenance_and_hash():
    record = AssetBuildRecord(
        asset_id="combat_helmet",
        build_id="bld_001",
        specification_hash="hash_spec_456",
        generator_versions={"ComponentizedHeroGenerator": "1.0.0"},
        parameters={"tint": "dark"},
        seed=10101,
        outputs=[{"mesh_id": "m_01", "triangles": 1200}],
        validation_results={"is_valid": True},
    )

    assert len(record.record_hash) == 64
    data = record.to_dict()
    assert data["asset_id"] == "combat_helmet"
    assert data["generator_versions"]["ComponentizedHeroGenerator"] == "1.0.0"
