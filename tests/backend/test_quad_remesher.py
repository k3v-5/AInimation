"""
Unit Tests for Studio Quad Remeshing and Topology Engine (backend.ai.quad_remesher).

Tests:
1. Planar triangle pairing to regular quads on primitive geometry.
2. Catmull-Clark subdivision converting arbitrary meshes into 100% pure quads.
3. Principal curvature tensor extraction and orthogonal tangent frame estimation.
4. Quad topology metrics (watertightness, aspect ratio, quad dominance).
5. Authentic Wavefront OBJ export with 4-vertex face primitives.
6. Khronos glTF 2.0 binary (.glb) export with aligned buffers and normals.
"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import numpy as np
import pytest

from backend.ai.quad_remesher import (
    QuadMesh,
    QuadTopologyStats,
    catmull_clark_subdivision,
    compute_vertex_normals,
    estimate_principal_curvatures,
    export_quad_glb,
    export_quad_obj,
    pair_triangles_to_quads,
    retopologize_to_quads,
)


@pytest.fixture
def triangulated_cube() -> Tuple[np.ndarray, np.ndarray]:
    """A standard unit cube centered at origin with 8 vertices and 12 triangles."""
    verts = np.array(
        [
            [-0.5, -0.5, -0.5],
            [0.5, -0.5, -0.5],
            [0.5, 0.5, -0.5],
            [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5],
            [0.5, -0.5, 0.5],
            [0.5, 0.5, 0.5],
            [-0.5, 0.5, 0.5],
        ],
        dtype=np.float32,
    )
    # 12 triangles
    tris = np.array(
        [
            # Back face (-Z)
            [0, 2, 1], [0, 3, 2],
            # Front face (+Z)
            [4, 5, 6], [4, 6, 7],
            # Bottom face (-Y)
            [0, 1, 5], [0, 5, 4],
            # Top face (+Y)
            [3, 6, 2], [3, 7, 6],
            # Left face (-X)
            [0, 4, 7], [0, 7, 3],
            # Right face (+X)
            [1, 2, 6], [1, 6, 5],
        ],
        dtype=np.int32,
    )
    return verts, tris


def test_triangle_pairing_on_cube(triangulated_cube: Tuple[np.ndarray, np.ndarray]) -> None:
    """Validate that 12 coplanar cube triangles are paired into 6 regular quads."""
    verts, tris = triangulated_cube
    quads, remaining_tris = pair_triangles_to_quads(verts, tris, max_dihedral_deg=30.0)

    assert len(quads) == 6
    assert len(remaining_tris) == 0
    assert quads.shape == (6, 4)


def test_catmull_clark_subdivision_pure_quads(triangulated_cube: Tuple[np.ndarray, np.ndarray]) -> None:
    """Validate Catmull-Clark subdivision produces 100% pure quad mesh with smooth topology."""
    verts, tris = triangulated_cube
    new_v, new_quads = catmull_clark_subdivision(verts, tris, iterations=1)

    assert len(new_v) > len(verts)
    assert len(new_quads) == len(tris) * 3  # Each triangle subdivides into 3 quads = 36 quads
    assert new_quads.shape[1] == 4

    # Run second iteration
    new_v2, new_quads2 = catmull_clark_subdivision(new_v, new_quads, iterations=1)
    assert len(new_quads2) == len(new_quads) * 4  # Each quad subdivides into 4 quads = 144 quads
    assert new_quads2.shape[1] == 4


def test_retopologize_to_quads_pipeline(triangulated_cube: Tuple[np.ndarray, np.ndarray]) -> None:
    """Validate high-level retopology API and topology stats."""
    verts, tris = triangulated_cube
    quad_mesh = retopologize_to_quads(verts, tris, target_quad_ratio=0.85)

    assert isinstance(quad_mesh, QuadMesh)
    assert quad_mesh.quad_count == 6
    assert quad_mesh.triangle_count == 0
    assert quad_mesh.quad_ratio == 1.0

    stats = quad_mesh.compute_stats()
    assert isinstance(stats, QuadTopologyStats)
    assert stats.quad_dominant_ratio == 1.0
    assert stats.is_watertight is True
    assert 0.8 <= stats.mean_aspect_ratio <= 1.5


def test_estimate_principal_curvatures(triangulated_cube: Tuple[np.ndarray, np.ndarray]) -> None:
    """Validate curvature tensor extraction and orthogonal tangent frame consistency."""
    verts, tris = triangulated_cube
    v_min, v_max = estimate_principal_curvatures(verts, tris)

    assert v_min.shape == verts.shape
    assert v_max.shape == verts.shape

    # Directions should be unit vectors
    lens_min = np.linalg.norm(v_min, axis=1)
    lens_max = np.linalg.norm(v_max, axis=1)
    assert np.allclose(lens_min, 1.0, atol=1e-3)
    assert np.allclose(lens_max, 1.0, atol=1e-3)

    # v_min and v_max must be orthogonal (dot product near 0)
    dots = np.sum(v_min * v_max, axis=1)
    assert np.all(np.abs(dots) < 0.1)


def test_export_quad_obj_format(tmp_path: Path, triangulated_cube: Tuple[np.ndarray, np.ndarray]) -> None:
    """Validate export to Wavefront OBJ with authentic 4-vertex quadrilateral faces."""
    verts, tris = triangulated_cube
    quad_mesh = retopologize_to_quads(verts, tris)

    out_obj = tmp_path / "test_cube_quads.obj"
    export_quad_obj(quad_mesh, out_obj)

    assert out_obj.exists()
    content = out_obj.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Verify quad faces: "f v1 v2 v3 v4" (4 index groups)
    f_lines = [l for l in lines if l.startswith("f ")]
    assert len(f_lines) == 6
    for f in f_lines:
        tokens = f.split()[1:]
        assert len(tokens) == 4, f"Expected 4 vertices per face, got: {f}"


def test_export_quad_glb_format(tmp_path: Path, triangulated_cube: Tuple[np.ndarray, np.ndarray]) -> None:
    """Validate export to Khronos glTF 2.0 binary (.glb) format with valid header and chunks."""
    verts, tris = triangulated_cube
    quad_mesh = retopologize_to_quads(verts, tris)

    out_glb = tmp_path / "test_cube_quads.glb"
    export_quad_glb(quad_mesh, out_glb)

    assert out_glb.exists()
    assert out_glb.stat().st_size > 100

    with open(out_glb, "rb") as f:
        magic, version, length = struct.unpack("<4sII", f.read(12))
        assert magic == b"glTF"
        assert version == 2
        assert length == out_glb.stat().st_size

        # Read JSON chunk
        chunk_len, chunk_type = struct.unpack("<II", f.read(8))
        assert chunk_type == 0x4E4F534A  # JSON
        json_data = json.loads(f.read(chunk_len).decode("utf-8"))
        assert "meshes" in json_data
        assert "accessors" in json_data
        assert "buffers" in json_data
