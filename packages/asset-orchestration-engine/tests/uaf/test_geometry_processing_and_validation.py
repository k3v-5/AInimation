"""
Tests for Geometry Processing (Topology, UV, LOD, Collision, Anatomy, Clothing Layers) and Validation.
UAF-81.3 Sections 25, 27, 33, 34, 47, 55, 59, 62, 64.
"""

from uaf.geometry.models.mesh_data import MeshData
from uaf.geometry.models.geometry_component import GeometryComponent
from uaf.geometry.anatomy.landmarks import LandmarkSystem
from uaf.geometry.anatomy.anatomy_profile import AnatomyProfile
from uaf.geometry.anatomy.socket import AttachmentSocket
from uaf.geometry.anatomy.clothing_layer import ClothingLayerSystem
from uaf.geometry.processing.topology import TopologyProcessor
from uaf.geometry.processing.uv import UVGenerator
from uaf.geometry.processing.lod import LODGenerator
from uaf.geometry.processing.collision import CollisionGenerator, CollisionType
from uaf.geometry.validation.geometry_validator import GeometryValidator


def test_landmark_system_default_humanoid():
    landmarks = LandmarkSystem.create_default_humanoid(height_meters=1.80)
    assert "pelvis" in landmarks.landmarks
    assert "head" in landmarks.landmarks
    assert "shoulder_L" in landmarks.landmarks
    assert "shoulder_R" in landmarks.landmarks
    assert landmarks.landmarks["head"][2] > landmarks.landmarks["pelvis"][2]


def test_anatomy_profile_validation():
    profile = AnatomyProfile(height_meters=1.85, shoulder_ratio=0.28)
    warnings = profile.validate_proportions()
    assert len(warnings) == 0

    extreme_profile = AnatomyProfile(height_meters=4.5)
    warnings_ext = extreme_profile.validate_proportions()
    assert len(warnings_ext) > 0


def test_clothing_layer_clearance():
    body = GeometryComponent("body", semantic_role="BODY", mesh_data=MeshData.create_cube(size=1.0))
    armor = GeometryComponent("armor", semantic_role="ARMOR", mesh_data=MeshData.create_cube(size=1.2))

    rep = ClothingLayerSystem.validate_layer_clearance(inner_component=body, outer_component=armor)
    assert rep.is_valid is True

    # Inverted layer hierarchy: body on top of armor
    inverted_rep = ClothingLayerSystem.validate_layer_clearance(inner_component=armor, outer_component=body)
    assert inverted_rep.is_valid is False
    assert any("Layer hierarchy violation" in v for v in inverted_rep.violations)


def test_topology_and_budget_analysis():
    cube = MeshData.create_cube(size=1.0)  # 12 triangles
    rep = TopologyProcessor.analyze(cube, max_triangle_budget=10)
    assert rep.budget_exceeded is True
    assert rep.is_manifold is True
    assert rep.is_valid is False

    rep_pass = TopologyProcessor.analyze(cube, max_triangle_budget=50)
    assert rep_pass.is_valid is True


def test_uv_generation_and_validation():
    cube = MeshData.create_cube(size=1.0)
    UVGenerator.generate_planar_uvs(cube)
    assert len(cube.uvs) == 8

    uv_rep = UVGenerator.validate_uvs(cube, texture_resolution=2048)
    assert uv_rep.is_valid is True
    assert uv_rep.has_uvs is True
    assert uv_rep.texel_density > 0


def test_lod_chain_generation():
    cube = MeshData.create_cube(size=1.0)
    lod_chain = LODGenerator.generate_lod_chain(cube, lod_count=3, reduction_per_level=0.5)

    assert lod_chain.lod_count == 3
    assert lod_chain.levels[0].lod_index == 0
    assert lod_chain.levels[0].triangle_count == 12
    assert lod_chain.levels[1].triangle_count <= lod_chain.levels[0].triangle_count


def test_collision_shape_generation():
    cube = MeshData.create_cube(size=2.0)
    box_col = CollisionGenerator.generate_from_mesh(cube, CollisionType.BOX, policy="character")
    assert box_col.shape_type == CollisionType.BOX
    assert box_col.dimensions == [2.0, 2.0, 2.0]
    assert box_col.policy == "character"

    capsule_col = CollisionGenerator.generate_from_mesh(cube, CollisionType.CAPSULE)
    assert capsule_col.shape_type == CollisionType.CAPSULE


def test_geometry_validator_comprehensive():
    cube = MeshData.create_cube(size=1.0)
    UVGenerator.generate_planar_uvs(cube)
    comp = GeometryComponent("comp_01", "ARMOR", mesh_data=cube)

    val_rep = GeometryValidator.validate_component(comp, max_triangle_budget=100)
    assert val_rep.is_valid is True
    assert len(val_rep.issues) == 0
