"""
Tests for Fabrication Anatomy, Proportions, Semantic Body Graph, and Garments.
UAF-81.10 Sections 3, 10, 15, 16, 65, 70.
"""

from uaf.fabrication.anatomy.proportions import (
    ProportionProfileType,
    ParametricAnatomy,
    ProportionProfile,
)
from uaf.fabrication.anatomy.body_graph import (
    FormLevel,
    BodyComponent,
    SemanticBodyGraph,
)
from uaf.fabrication.garments.garment import (
    GarmentLayer,
    GarmentDefinition,
)


def test_proportions_and_parametric_anatomy():
    profile = ProportionProfile.create_heroic_profile("Prop_Hero_01")
    assert profile.profile_type == ProportionProfileType.HEROIC
    assert profile.anatomy.height_cm == 188.0
    assert profile.anatomy.shoulder_width_cm == 54.0
    data = profile.to_dict()
    assert data["profile_id"] == "Prop_Hero_01"
    assert data["profile_type"] == "HEROIC"


def test_semantic_body_graph_and_form_levels():
    graph = SemanticBodyGraph.create_standard_humanoid_graph("Char_Warrior")
    assert len(graph.components) == 7
    primary = graph.get_components_by_level(FormLevel.PRIMARY)
    assert len(primary) == 7
    assert len(graph.graph_hash) == 64

    # Add secondary component
    graph.add_component(
        BodyComponent(
            component_id="body.shoulder_armor",
            form_level=FormLevel.SECONDARY,
            parent_id="body.torso",
            material_region_id="MAT_STEEL",
            is_rigid=True,
        )
    )
    assert len(graph.components) == 8
    assert graph.components["body.shoulder_armor"].is_rigid is True


def test_garment_definition_and_layers():
    chestplate = GarmentDefinition.create_tactical_chestplate("Arm_Plates_01")
    assert chestplate.layer == GarmentLayer.ARMOR_PLATE
    assert chestplate.layer.value == 3
    assert chestplate.is_rigid is True
    assert "body.torso" in chestplate.target_body_components
    data = chestplate.to_dict()
    assert data["layer"] == 3
