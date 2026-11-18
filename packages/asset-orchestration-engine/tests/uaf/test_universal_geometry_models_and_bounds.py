"""
Tests for Universal Geometry Models, Dimensions, and Topology Counts.
UAF-81.53 Sections 3, 4, 5, 6, 164, 166.
"""

from uaf.universal_geometry.models.definition import (
    MeshCategory53,
    TopologyType53,
    MeshDimensions53,
    UniversalMeshSpecification,
)


def test_mesh_dimensions_and_validity():
    dims_ok = MeshDimensions53(width_cm=100.0, length_cm=100.0, height_cm=100.0)
    assert dims_ok.is_valid is True

    dims_zero = MeshDimensions53(width_cm=100.0, length_cm=0.0, height_cm=100.0)
    assert dims_zero.is_valid is False

    dims_neg = MeshDimensions53(width_cm=-10.0, length_cm=50.0, height_cm=50.0)
    assert dims_neg.is_valid is False


def test_universal_mesh_specification_and_hashing():
    spec = UniversalMeshSpecification(
        mesh_id="Mesh_Test_Vehicle",
        category=MeshCategory53.VEHICLE,
        topology=TopologyType53.TRIANGLES,
        dimensions=MeshDimensions53(width_cm=200.0, length_cm=450.0, height_cm=150.0),
        vertex_count=5000,
        triangle_count=10000,
        has_normals=True,
        has_tangents=True,
        has_uv=True,
        has_collision=True,
        has_lod=True,
        is_nanite_ready=True,
        seed=998877,
    )

    assert spec.is_valid_mesh is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["category"] == "VEHICLE"
    assert data["triangle_count"] == 10000

    bad_spec_tri = UniversalMeshSpecification(
        mesh_id="Mesh_NoTriangles",
        category=MeshCategory53.PROP,
        vertex_count=1,  # < 3
        triangle_count=0,  # < 1
    )
    assert bad_spec_tri.is_valid_mesh is False
