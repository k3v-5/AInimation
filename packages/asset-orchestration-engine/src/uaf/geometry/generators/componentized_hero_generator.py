"""
ComponentizedHeroGenerator synthesizes fully decoupled, multi-component character assemblies.
UAF-81.3 Sections 87, 88, 93, 101, 102.
"""

from typing import Dict, Any, Optional
from ..models.geometry_component import GeometryComponent
from ..models.mesh_data import MeshData
from ..models.transform import Transform3D
from ..assembly.character_assembly import ComponentizedCharacter
from ..anatomy.landmarks import LandmarkSystem
from ..anatomy.socket import AttachmentSocket
from ..processing.uv import UVGenerator
from .generator_interface import GeometryGenerator
from ...core.specification.asset_specification import AssetSpecification


class ComponentizedHeroGenerator(GeometryGenerator):
    """
    High-fidelity character generator constructing discrete components:
    Body, Head, Face, Eyes, Teeth, Hair, Clothing, Armor, Weapon, and Accessories.
    """
    def __init__(self, name: str = "ComponentizedHeroGenerator"):
        self.name = name

    def generate(self, spec: AssetSpecification, parameters: Optional[Dict[str, Any]] = None) -> GeometryComponent:
        char_assembly = self.generate_character_assembly(spec, parameters)
        return char_assembly.root

    def generate_character_assembly(
        self,
        spec: AssetSpecification,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ComponentizedCharacter:
        params = parameters or spec.parameters
        h = float(params.get("height", 1.85))

        # Root Component
        root = GeometryComponent(
            component_id=f"root_{spec.identity.asset_id}",
            semantic_role="STRUCTURAL",
            transform=Transform3D(position=[0.0, 0.0, 0.0]),
            quality_level="hero",
        )

        # 1. Body Component (Torso + Limbs)
        body_mesh = MeshData.create_cube(size=h * 0.4)
        UVGenerator.generate_planar_uvs(body_mesh)
        body_comp = GeometryComponent(
            component_id="comp_body",
            semantic_role="TORSO",
            transform=Transform3D(position=[0.0, 0.0, h * 0.55]),
            mesh_data=body_mesh,
            material_slots=["mat_body_skin"],
        )
        root.add_child(body_comp)

        # 2. Head Component
        head_mesh = MeshData.create_cube(size=h * 0.16)
        UVGenerator.generate_planar_uvs(head_mesh)
        head_comp = GeometryComponent(
            component_id="comp_head",
            semantic_role="HEAD",
            transform=Transform3D(position=[0.0, 0.0, h * 0.9]),
            mesh_data=head_mesh,
            material_slots=["mat_head_skin"],
        )
        root.add_child(head_comp)

        # 2a. Face (independent child of Head)
        face_mesh = MeshData.create_cube(size=h * 0.1)
        UVGenerator.generate_planar_uvs(face_mesh)
        face_comp = GeometryComponent(
            component_id="comp_face",
            semantic_role="HEAD",
            transform=Transform3D(position=[0.0, h * 0.08, 0.0]),
            mesh_data=face_mesh,
            material_slots=["mat_facial_complex"],
        )
        head_comp.add_child(face_comp)

        # 2b. Eyes
        eyes_mesh = MeshData.create_cube(size=h * 0.03)
        eyes_comp = GeometryComponent(
            component_id="comp_eyes",
            semantic_role="HEAD",
            transform=Transform3D(position=[0.0, h * 0.09, h * 0.03]),
            mesh_data=eyes_mesh,
            material_slots=["mat_eyes_cornea"],
        )
        head_comp.add_child(eyes_comp)

        # 2c. Teeth
        teeth_mesh = MeshData.create_cube(size=h * 0.02)
        teeth_comp = GeometryComponent(
            component_id="comp_teeth",
            semantic_role="HEAD",
            transform=Transform3D(position=[0.0, h * 0.07, -h * 0.02]),
            mesh_data=teeth_mesh,
            material_slots=["mat_teeth"],
        )
        head_comp.add_child(teeth_comp)

        # 3. Hair Component
        hair_mesh = MeshData.create_cube(size=h * 0.17)
        UVGenerator.generate_planar_uvs(hair_mesh)
        hair_comp = GeometryComponent(
            component_id="comp_hair",
            semantic_role="DECORATIVE",
            transform=Transform3D(position=[0.0, 0.0, h * 0.95]),
            mesh_data=hair_mesh,
            material_slots=["mat_hair_strands"],
        )
        root.add_child(hair_comp)

        # 4. Clothing Component
        clothing_mesh = MeshData.create_cube(size=h * 0.42)
        UVGenerator.generate_planar_uvs(clothing_mesh)
        clothing_comp = GeometryComponent(
            component_id="comp_clothing",
            semantic_role="CLOTHING",
            transform=Transform3D(position=[0.0, 0.0, h * 0.54]),
            mesh_data=clothing_mesh,
            material_slots=["mat_fabric_tactical"],
        )
        root.add_child(clothing_comp)

        # 5. Armor Component
        armor_mesh = MeshData.create_cube(size=h * 0.45)
        UVGenerator.generate_planar_uvs(armor_mesh)
        armor_comp = GeometryComponent(
            component_id="comp_armor",
            semantic_role="ARMOR",
            transform=Transform3D(position=[0.0, 0.0, h * 0.56]),
            mesh_data=armor_mesh,
            material_slots=["mat_heavy_armor_plates"],
        )
        root.add_child(armor_comp)

        # 6. Weapon Component
        weapon_mesh = MeshData.create_cube(size=h * 0.5)
        weapon_comp = GeometryComponent(
            component_id="comp_weapon",
            semantic_role="WEAPON",
            transform=Transform3D(position=[h * 0.25, h * 0.1, h * 0.4]),
            mesh_data=weapon_mesh,
            material_slots=["mat_plasma_rifle"],
        )
        root.add_child(weapon_comp)

        # Sockets
        sockets = {
            "hand_R_socket": AttachmentSocket("hand_R_socket", position=[h * 0.25, 0.0, h * 0.4], allowed_categories=["WEAPON"]),
            "back_socket": AttachmentSocket("back_socket", position=[0.0, -h * 0.15, h * 0.65], allowed_categories=["WEAPON", "ACCESSORY"]),
            "head_socket": AttachmentSocket("head_socket", position=[0.0, 0.0, h * 0.98], allowed_categories=["ACCESSORY", "HELMET"]),
        }

        return ComponentizedCharacter(
            character_id=spec.identity.asset_id,
            root=root,
            landmarks=LandmarkSystem.create_default_humanoid(height_meters=h),
            sockets=sockets,
        )
