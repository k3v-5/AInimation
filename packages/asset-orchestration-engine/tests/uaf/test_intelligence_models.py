"""
Tests for UAF-81.1 Semantic Models:
SemanticAsset, ComplexityLevel, CharacterSemanticModel, MaterialSemanticModel,
TextureSetSemanticModel, ModularKitSemanticModel, WorldSemanticModel.
UAF-81.1 Sections 4, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 44.
"""

from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.identity.asset_types import AssetType
from uaf.intelligence.models.complexity_level import ComplexityLevel
from uaf.intelligence.models.semantic_asset import SemanticAsset
from uaf.intelligence.models.character_semantic import CharacterSemanticModel, ANATOMICAL_REGIONS
from uaf.intelligence.models.material_semantic import MaterialSemanticModel, MaterialLayer
from uaf.intelligence.models.texture_semantic import TextureSetSemanticModel, TextureMapSpecification
from uaf.intelligence.models.modular_semantic import ModularKitSemanticModel, ModularModule, ConnectionSocket
from uaf.intelligence.models.world_semantic import EnvironmentSemanticModel, WorldSemanticModel, LevelSemanticModel


def test_semantic_asset_layers_and_intent_hash():
    identity = AssetIdentity(asset_id="hero_01", asset_type=AssetType.CHARACTER)
    asset = SemanticAsset(
        identity=identity,
        intent={"role": "heavy_infantry", "mood": "intimidating"},
        structure={"regions": ["head", "torso", "limbs"]},
        appearance={"style": "brutalist_military"},
        behavior={"interaction": "talk", "combat": "assault"},
        complexity_level=ComplexityLevel.C4_HERO,
    )

    assert asset.complexity_level == ComplexityLevel.C4_HERO
    assert len(asset.intent_hash) == 64

    data = asset.to_dict()
    reconstructed = SemanticAsset.from_dict(data)
    assert reconstructed.identity.asset_id == "hero_01"
    assert reconstructed.complexity_level == ComplexityLevel.C4_HERO
    assert reconstructed.intent_hash == asset.intent_hash


def test_character_semantic_anatomical_regions():
    char = CharacterSemanticModel(
        height_meters=1.85,
        build="heavy",
        facial_fidelity="high",
        clothing_complexity="high",
        armor_tier="heavy_modular",
    )
    for region in ["head", "torso", "hand_L", "hand_R", "foot_L", "foot_R"]:
        assert region in char.anatomical_regions
    assert char.height_meters == 1.85


def test_material_semantic_layers():
    mat = MaterialSemanticModel(
        material_name="military_painted_steel",
        base_color="#334455",
        metallic=0.9,
        roughness=0.3,
        layers=[
            MaterialLayer(name="base_steel", layer_type="base", opacity=1.0),
            MaterialLayer(name="olive_paint", layer_type="primary_surface", opacity=0.95),
            MaterialLayer(name="edge_wear", layer_type="wear", opacity=0.7),
            MaterialLayer(name="battle_scratches", layer_type="damage", opacity=0.4),
        ],
    )
    assert len(mat.layers) == 4
    assert mat.layers[2].layer_type == "wear"
    data = mat.to_dict()
    assert len(data["layers"]) == 4


def test_texture_set_semantic_spec():
    tex_set = TextureSetSemanticModel(
        set_name="heavy_armor_textures",
        target_resolution=4096,
        maps={
            "albedo": TextureMapSpecification("albedo", 4096, "PNG", "sRGB"),
            "normal": TextureMapSpecification("normal", 4096, "PNG", "Linear"),
            "roughness": TextureMapSpecification("roughness", 4096, "PNG", "Linear"),
        },
    )
    assert tex_set.target_resolution == 4096
    assert tex_set.maps["albedo"].color_space == "sRGB"
    assert tex_set.maps["normal"].color_space == "Linear"


def test_modular_kit_socket_compatibility():
    socket_a = ConnectionSocket(
        socket_id="s1",
        socket_type="wall_edge_v1",
        position=[0, 0, 0],
        direction=[1, 0, 0],
        compatible_types=["wall_edge_v1", "corner_edge_v1"],
    )
    socket_b = ConnectionSocket(
        socket_id="s2",
        socket_type="corner_edge_v1",
        position=[0, 0, 0],
        direction=[-1, 0, 0],
        compatible_types=["wall_edge_v1"],
    )
    socket_incompatible = ConnectionSocket(
        socket_id="s3",
        socket_type="roof_socket",
        position=[0, 0, 0],
        direction=[0, 0, 1],
        compatible_types=["roof_mount"],
    )

    assert socket_a.is_compatible_with(socket_b) is True
    assert socket_a.is_compatible_with(socket_incompatible) is False


def test_world_environment_level_models():
    env = EnvironmentSemanticModel(name="desert_wasteland", biome="industrial_desert", terrain_type="rocky_sand")
    world = WorldSemanticModel(world_name="planet_vulcan", scale="planetary", region_count=6, biomes=["desert", "canyon"])
    level = LevelSemanticModel(level_name="outpost_bravo", spawn_zones=["zone_a", "zone_b"], streaming_budget_mb=1024.0)

    assert env.biome == "industrial_desert"
    assert world.region_count == 6
    assert len(level.spawn_zones) == 2
