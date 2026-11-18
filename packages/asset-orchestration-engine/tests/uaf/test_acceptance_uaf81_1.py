"""
UAF-81.1 Acceptance Tests (Sections 58, 59, 60, 61, 70).
Verifies:
- Section 58: Character (C4 Hero Character represented without Blender primitives)
- Section 59: Material (Industrial Painted Metal represented without concrete shader nodes)
- Section 60: Modular Kit (Industrial Facility modular kit with grid and sockets)
- Section 61: World (Abandoned Industrial Planet with regions and streaming)
"""

from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.identity.asset_types import AssetType
from uaf.core.specification.asset_specification import AssetSpecification
from uaf.intelligence.compiler.resolution_pipeline import ResolutionPipeline
from uaf.intelligence.models.semantic_asset import SemanticAsset
from uaf.intelligence.models.complexity_level import ComplexityLevel
from uaf.intelligence.models.character_semantic import CharacterSemanticModel
from uaf.intelligence.models.material_semantic import MaterialSemanticModel, MaterialLayer
from uaf.intelligence.models.modular_semantic import ModularKitSemanticModel, ModularModule, ConnectionSocket
from uaf.intelligence.models.world_semantic import WorldSemanticModel, EnvironmentSemanticModel


def test_acceptance_section_58_c4_hero_character():
    """
    Acceptance Test Section 58:
    A complex C4 Hero Character must be fully expressed semantically
    WITHOUT specifying Blender primitives or modifier tricks.
    """
    pipeline = ResolutionPipeline()

    spec = AssetSpecification(
        identity=AssetIdentity(
            asset_id="soldier_tactical_scifi",
            asset_type=AssetType.CHARACTER,
            namespace="production_squad",
            version="1.0.0",
        ),
        target="unreal_engine_5.5",
        quality_profile="production",
        parameters={
            "archetype": "HumanoidCharacter",
            "species": "humanoid",
            "height": "1.85m",
            "complexity": "C4",
            "style": "realistic_scifi",
            "anatomical_fidelity": "high",
            "facial_fidelity": "high",
            "clothing_complexity": "high",
            "armor": "modular_heavy",
            "surface_detail": "high",
            "textures": "4K",
            "rig": "humanoid_production",
        },
        seed=81101,
    )

    resolved = pipeline.resolve(spec)

    # Verifications:
    assert resolved.resolved_parameters["height"] == 1.85
    assert resolved.effective_quality_profile == "production"
    assert resolved.effective_target_profile == "unreal_engine_5.5"

    # Must have extracted the required capabilities dynamically without binding to Blender
    required = resolved.required_capabilities
    assert "organic_surface_generation" in required
    assert "skeletal_rigging" in required
    assert "advanced_facial_generation" in required
    assert "cloth_geometry" in required
    assert "high_detail_surface" in required


def test_acceptance_section_59_material():
    """
    Acceptance Test Section 59:
    An Industrial Painted Metal material must be expressed semantically
    without binding to concrete rendering/shader graph nodes.
    """
    mat_spec = MaterialSemanticModel(
        material_name="industrial_painted_metal",
        base_color="#2b2d2f",
        metallic=0.92,
        roughness=0.45,
        layers=[
            MaterialLayer(name="base_substrate", layer_type="base", opacity=1.0, properties={"metal": "steel"}),
            MaterialLayer(name="primer_coat", layer_type="primary_surface", opacity=0.9, properties={"color": "#666666"}),
            MaterialLayer(name="top_paint", layer_type="primary_surface", opacity=0.95, properties={"color": "#2b2d2f"}),
            MaterialLayer(name="edge_wear", layer_type="wear", opacity=0.8, properties={"intensity": "high"}),
            MaterialLayer(name="surface_scratches", layer_type="damage", opacity=0.5, properties={"depth": "medium"}),
            MaterialLayer(name="dust_accumulation", layer_type="dirt", opacity=0.35, properties={"spread": "crevices"}),
        ],
    )

    data = mat_spec.to_dict()
    assert data["material_name"] == "industrial_painted_metal"
    assert data["metallic"] == 0.92
    assert len(data["layers"]) == 6
    assert data["layers"][3]["layer_type"] == "wear"
    assert data["layers"][4]["layer_type"] == "damage"


def test_acceptance_section_60_modular_kit():
    """
    Acceptance Test Section 60:
    Modular kit 'Industrial Facility' with 1m grid, sockets, and standard modules.
    """
    kit = ModularKitSemanticModel(
        kit_name="industrial_facility_kit",
        grid_size_meters=1.0,
        modules={
            "wall_std": ModularModule(
                module_id="mod_wall_std",
                module_type="wall",
                dimensions_meters=[2.0, 3.0, 0.2],
                sockets=[
                    ConnectionSocket("s_left", "wall_snap", [-1.0, 0.0, 0.0], [-1, 0, 0], ["wall_snap"]),
                    ConnectionSocket("s_right", "wall_snap", [1.0, 0.0, 0.0], [1, 0, 0], ["wall_snap"]),
                ],
                variants=["plain", "window", "doorway"],
            ),
            "corner_90": ModularModule(
                module_id="mod_corner_90",
                module_type="corner",
                dimensions_meters=[1.0, 3.0, 1.0],
                sockets=[
                    ConnectionSocket("s_c1", "wall_snap", [0.0, 0.0, -0.5], [0, 0, -1], ["wall_snap"]),
                    ConnectionSocket("s_c2", "wall_snap", [0.5, 0.0, 0.0], [1, 0, 0], ["wall_snap"]),
                ],
            ),
        },
    )

    data = kit.to_dict()
    assert data["grid_size_meters"] == 1.0
    assert "wall_std" in data["modules"]
    assert len(data["modules"]["wall_std"]["sockets"]) == 2
    assert data["modules"]["wall_std"]["variants"] == ["plain", "window", "doorway"]


def test_acceptance_section_61_world():
    """
    Acceptance Test Section 61:
    World 'Abandoned Industrial Planet' with 6 regions, wasteland biomes, and streaming requirements.
    """
    world = WorldSemanticModel(
        world_name="abandoned_industrial_planet",
        scale="planetary_scale",
        region_count=6,
        biomes=["industrial_wasteland", "toxic_canyons", "scrap_plains"],
        requires_streaming=True,
        gameplay_spaces=["refinery_hub", "extraction_site_alpha"],
    )

    data = world.to_dict()
    assert data["world_name"] == "abandoned_industrial_planet"
    assert data["region_count"] == 6
    assert len(data["biomes"]) == 3
    assert data["requires_streaming"] is True
