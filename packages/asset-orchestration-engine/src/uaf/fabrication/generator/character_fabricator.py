"""
ProceduralCharacterFabricator synthesizes complex multi-component characters across all archetypes.
UAF-81.10 Sections 26, 30, 128, 164, 165.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..anatomy.proportions import ProportionProfile, ProportionProfileType, ParametricAnatomy
from ..anatomy.body_graph import FormLevel, BodyComponent, SemanticBodyGraph
from ..garments.garment import GarmentLayer, GarmentDefinition


class TopologyStrategyType(str, Enum):
    DEFORMATION = "DEFORMATION"
    HARD_SURFACE = "HARD_SURFACE"
    ORGANIC = "ORGANIC"
    HYBRID = "HYBRID"
    NANITE = "NANITE"


class FabricationQuality(str, Enum):
    DRAFT = "DRAFT"
    STANDARD = "STANDARD"
    HIGH = "HIGH"
    HERO = "HERO"
    CINEMATIC = "CINEMATIC"


class ProceduralCharacterFabricator:
    """
    Fabricates character structures adhering strictly to Section 30:
    NO GLOBAL REMESH RULE - components maintain distinct logical boundaries.
    """

    @classmethod
    def build_organic_humanoid(cls, character_id: str, seed: int = 42) -> SemanticBodyGraph:
        """1. Organic Humanoid (naked / biological skin)."""
        graph = SemanticBodyGraph.create_standard_humanoid_graph(character_id)
        # Secondary muscular masses
        graph.add_component(BodyComponent(f"{character_id}.muscles_pectoral", FormLevel.SECONDARY, "body.torso", "MAT_SKIN"))
        graph.add_component(BodyComponent(f"{character_id}.face_features", FormLevel.SECONDARY, "body.head", "MAT_HEAD"))
        return graph

    @classmethod
    def build_clothed_humanoid(
        cls,
        character_id: str,
        seed: int = 42,
    ) -> tuple[SemanticBodyGraph, List[GarmentDefinition]]:
        """2. Clothed Humanoid (fabric garments on body)."""
        graph = SemanticBodyGraph.create_standard_humanoid_graph(character_id)
        jacket = GarmentDefinition(
            garment_id=f"{character_id}_jacket",
            name="Tactical Combat Jacket",
            layer=GarmentLayer.OUTER_GARMENT,
            target_body_components=["body.torso", "body.arm_L", "body.arm_R"],
            material_family="TACTICAL_FABRIC",
            thickness_cm=0.4,
        )
        pants = GarmentDefinition(
            garment_id=f"{character_id}_pants",
            name="Cargo Pants",
            layer=GarmentLayer.OUTER_GARMENT,
            target_body_components=["body.pelvis", "body.leg_L", "body.leg_R"],
            material_family="CANVAS",
            thickness_cm=0.3,
        )
        return graph, [jacket, pants]

    @classmethod
    def build_armored_humanoid(
        cls,
        character_id: str,
        seed: int = 42,
    ) -> tuple[SemanticBodyGraph, List[GarmentDefinition]]:
        """3. Armored Humanoid (hard-surface plates on inner suit)."""
        graph = SemanticBodyGraph.create_standard_humanoid_graph(character_id)
        undersuit = GarmentDefinition(
            garment_id=f"{character_id}_undersuit",
            name="Thermal Undersuit",
            layer=GarmentLayer.INNER_LAYER,
            target_body_components=["body.torso", "body.leg_L", "body.leg_R"],
            material_family="NEOPRENE",
        )
        cuirass = GarmentDefinition(
            garment_id=f"{character_id}_cuirass",
            name="Polymer Cuirass",
            layer=GarmentLayer.ARMOR_PLATE,
            target_body_components=["body.torso"],
            material_family="COMPOSITE_ARMOR",
            is_rigid=True,
        )
        return graph, [undersuit, cuirass]

    @classmethod
    def build_mechanical_character(cls, character_id: str, seed: int = 42) -> SemanticBodyGraph:
        """4. Mechanical Robot (fully rigid chassis)."""
        graph = SemanticBodyGraph(character_id=character_id)
        graph.add_component(BodyComponent("chassis.torso", FormLevel.PRIMARY, None, "MAT_STEEL", is_rigid=True))
        graph.add_component(BodyComponent("chassis.head_sensor", FormLevel.PRIMARY, "chassis.torso", "MAT_SENSORS", is_rigid=True))
        graph.add_component(BodyComponent("chassis.actuator_L", FormLevel.PRIMARY, "chassis.torso", "MAT_STEEL", is_rigid=True))
        graph.add_component(BodyComponent("chassis.actuator_R", FormLevel.PRIMARY, "chassis.torso", "MAT_STEEL", is_rigid=True))
        graph.add_component(BodyComponent("chassis.hydraulics", FormLevel.SECONDARY, "chassis.torso", "MAT_CHROME", is_rigid=True))
        return graph

    @classmethod
    def build_creature(cls, character_id: str, seed: int = 42) -> SemanticBodyGraph:
        """5. Organic Quadruped / Beast Creature."""
        graph = SemanticBodyGraph(character_id=character_id)
        graph.add_component(BodyComponent("creature.torso", FormLevel.PRIMARY, None, "MAT_HIDE"))
        graph.add_component(BodyComponent("creature.neck_head", FormLevel.PRIMARY, "creature.torso", "MAT_HIDE"))
        graph.add_component(BodyComponent("creature.tail", FormLevel.PRIMARY, "creature.torso", "MAT_HIDE"))
        graph.add_component(BodyComponent("creature.leg_FL", FormLevel.PRIMARY, "creature.torso", "MAT_HIDE"))
        graph.add_component(BodyComponent("creature.leg_FR", FormLevel.PRIMARY, "creature.torso", "MAT_HIDE"))
        graph.add_component(BodyComponent("creature.leg_BL", FormLevel.PRIMARY, "creature.torso", "MAT_HIDE"))
        graph.add_component(BodyComponent("creature.leg_BR", FormLevel.PRIMARY, "creature.torso", "MAT_HIDE"))
        graph.add_component(BodyComponent("creature.horns", FormLevel.SECONDARY, "creature.neck_head", "MAT_BONE", is_rigid=True))
        return graph

    @classmethod
    def build_hybrid_character(
        cls,
        character_id: str,
        seed: int = 42,
    ) -> tuple[SemanticBodyGraph, List[GarmentDefinition]]:
        """6. Hybrid Character (Cyborg / Organic + Cybernetic limb + Gear)."""
        graph = SemanticBodyGraph.create_standard_humanoid_graph(character_id)
        # Replace right arm with cybernetic mechanical limb
        graph.components["body.arm_R"].is_rigid = True
        graph.components["body.arm_R"].material_region_id = "MAT_CYBERNETIC_ALLOY"

        tactical_vest = GarmentDefinition(
            garment_id=f"{character_id}_vest",
            name="Tactical Loadout Vest",
            layer=GarmentLayer.TACTICAL_RIG,
            target_body_components=["body.torso"],
            material_family="BALLISTIC_NYLON",
        )
        return graph, [tactical_vest]
