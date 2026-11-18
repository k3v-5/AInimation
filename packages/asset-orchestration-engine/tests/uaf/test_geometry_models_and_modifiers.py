"""
Tests for Geometry Models, Bounding Volumes, MeshData, and Modifier Stack.
UAF-81.3 Sections 4, 12, 14, 20, 21, 22, 67.
"""

from uaf.geometry.models.transform import Transform3D
from uaf.geometry.models.bounding_volume import AABB, BoundingSphere
from uaf.geometry.models.mesh_data import MeshData
from uaf.geometry.models.geometry_component import GeometryComponent
from uaf.geometry.modifiers.modifier import ModifierType, ProceduralModifier, ModifierStack


def test_transform_defaults_and_serialization():
    t = Transform3D(position=[1.0, 2.0, 3.0], scale=[2.0, 2.0, 2.0])
    data = t.to_dict()
    assert data["position"] == [1.0, 2.0, 3.0]
    assert data["scale"] == [2.0, 2.0, 2.0]

    reconstructed = Transform3D.from_dict(data)
    assert reconstructed.position == [1.0, 2.0, 3.0]
    assert reconstructed.scale == [2.0, 2.0, 2.0]


def test_aabb_calculations_and_intersection():
    aabb1 = AABB(min_point=[-1.0, -1.0, -1.0], max_point=[1.0, 1.0, 1.0])
    aabb2 = AABB(min_point=[0.5, 0.5, 0.5], max_point=[2.0, 2.0, 2.0])
    aabb_far = AABB(min_point=[5.0, 5.0, 5.0], max_point=[6.0, 6.0, 6.0])

    assert aabb1.dimensions == [2.0, 2.0, 2.0]
    assert aabb1.center == [0.0, 0.0, 0.0]
    assert aabb1.intersects(aabb2) is True
    assert aabb1.intersects(aabb_far) is False


def test_mesh_data_cube_creation_and_topology():
    cube = MeshData.create_cube(size=2.0)
    assert cube.vertex_count == 8
    assert cube.face_count == 6
    assert cube.triangle_count == 12  # 6 quads = 12 triangles
    assert cube.is_manifold() is True
    assert cube.has_degenerate_faces() is False
    assert len(cube.normals) == 6

    aabb = cube.calculate_aabb()
    assert aabb.dimensions == [2.0, 2.0, 2.0]


def test_mesh_data_degenerate_and_non_manifold_detection():
    # Degenerate face with duplicate vertex index
    bad_mesh = MeshData(
        vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        faces=[[0, 1, 1]],  # Duplicate index 1
    )
    assert bad_mesh.has_degenerate_faces() is True

    # Non-manifold edge shared by 3 faces
    nm_mesh = MeshData(
        vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1]],
        faces=[
            [0, 1, 2],  # Edge (0, 1)
            [0, 1, 3],  # Edge (0, 1)
            [0, 1, 4],  # Edge (0, 1) -> 3 faces sharing edge (0, 1)!
        ],
    )
    assert nm_mesh.is_manifold() is False


def test_geometry_component_hierarchy_and_triangle_count():
    root = GeometryComponent(
        component_id="root",
        semantic_role="STRUCTURAL",
        mesh_data=MeshData.create_cube(size=1.0),  # 12 tris
    )
    child = GeometryComponent(
        component_id="head",
        semantic_role="HEAD",
        mesh_data=MeshData.create_cube(size=0.5),  # 12 tris
        transform=Transform3D(position=[0.0, 0.0, 1.5]),
    )
    root.add_child(child)

    assert root.total_triangle_count == 24
    assert root.find_component("head") is child

    combined_aabb = root.calculate_combined_aabb()
    # Z goes from -0.5 to (1.5 + 0.25) = 1.75
    assert combined_aabb.max_point[2] == 1.75


def test_modifier_stack_decimate_and_mirror():
    cube = MeshData.create_cube(size=1.0)
    stack = ModifierStack()
    stack.add_modifier(ProceduralModifier("mod_decimate", ModifierType.DECIMATE, {"ratio": 0.5}))

    decimated = stack.apply_to(cube)
    assert decimated.face_count == 3  # 6 * 0.5 = 3 faces

    mirror_stack = ModifierStack()
    mirror_stack.add_modifier(ProceduralModifier("mod_mirror", ModifierType.MIRROR, {"axis": "X"}))
    mirrored = mirror_stack.apply_to(cube)
    assert mirrored.vertex_count == 16  # 8 original + 8 mirrored
    assert mirrored.face_count == 12    # 6 original + 6 mirrored
