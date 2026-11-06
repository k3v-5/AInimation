"""
Unit Tests for Studio PBR High-to-Low Poly Texture Baker (backend.ai.pbr_baker).

Tests:
1. MikkTSpace Gram-Schmidt orthogonal TBN frame calculation.
2. High-poly curvature and ambient occlusion factor extraction.
3. High-to-low poly baking pipeline producing Tangent Normal, AO, Cavity, and ORM textures.
4. Channel validation (OpenGL normal standard: flat surface = (128, 128, 255)).
5. Pydantic v2 strict schema validation on BakeConfig and BakedPBRMaps.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from backend.ai.pbr_baker import (
    BakeConfig,
    BakedPBRMaps,
    bake_high_to_low_pbr,
    compute_mesh_tangents,
    compute_surface_curvature_and_ao,
)


@pytest.fixture
def low_poly_quad_plane() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A flat quad plane (4 vertices, 1 quad, 4 UV coordinates)."""
    verts = np.array(
        [
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )
    quads = np.array([[0, 1, 2, 3]], dtype=np.int32)
    uvs = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ],
        dtype=np.float32,
    )
    return verts, quads, uvs


@pytest.fixture
def dense_high_poly_relief() -> Tuple[np.ndarray, np.ndarray]:
    """A dense grid of vertices with high-frequency sinusoidal ripple detail."""
    grid_size = 32
    xs = np.linspace(-1.0, 1.0, grid_size, dtype=np.float32)
    ys = np.linspace(-1.0, 1.0, grid_size, dtype=np.float32)
    gx, gy = np.meshgrid(xs, ys)

    # Sine ripple detail
    gz = 0.08 * np.sin(gx * 12.0) * np.cos(gy * 12.0)
    verts = np.stack([gx.flatten(), gy.flatten(), gz.flatten()], axis=-1).astype(np.float32)

    # Compute analytical surface normals from gradient
    dz_dx = 0.08 * 12.0 * np.cos(gx * 12.0) * np.cos(gy * 12.0)
    dz_dy = -0.08 * 12.0 * np.sin(gx * 12.0) * np.sin(gy * 12.0)
    nx = -dz_dx.flatten()
    ny = -dz_dy.flatten()
    nz = np.ones_like(nx)
    lens = np.sqrt(nx**2 + ny**2 + nz**2)
    normals = np.stack([nx / lens, ny / lens, nz / lens], axis=-1).astype(np.float32)

    return verts, normals


def test_compute_mesh_tangents(low_poly_quad_plane: Tuple[np.ndarray, np.ndarray, np.ndarray]) -> None:
    """Verify that vertex TBN frames are mutually orthogonal and normalized."""
    verts, faces, uvs = low_poly_quad_plane
    tangents, bitangents, normals = compute_mesh_tangents(verts, faces, uvs)

    assert tangents.shape == (4, 3)
    assert bitangents.shape == (4, 3)
    assert normals.shape == (4, 3)

    # Normals point strictly up along +Z
    assert np.allclose(normals[:, 2], 1.0, atol=1e-3)

    # Tangents point along +X (UV U-direction)
    assert np.allclose(tangents[:, 0], 1.0, atol=1e-3)

    # Bitangents point along +Y (UV V-direction)
    assert np.allclose(bitangents[:, 1], 1.0, atol=1e-3)

    # Tangents and normals must be orthogonal (dot = 0)
    dots_tn = np.sum(tangents * normals, axis=1)
    assert np.allclose(dots_tn, 0.0, atol=1e-4)

    # Bitangents and normals must be orthogonal
    dots_bn = np.sum(bitangents * normals, axis=1)
    assert np.allclose(dots_bn, 0.0, atol=1e-4)


def test_surface_curvature_and_ao(dense_high_poly_relief: Tuple[np.ndarray, np.ndarray]) -> None:
    """Verify curvature and AO metrics on undulating high-poly surface."""
    verts, normals = dense_high_poly_relief
    curv, ao = compute_surface_curvature_and_ao(verts, normals, k_neighbors=12)

    assert len(curv) == len(verts)
    assert len(ao) == len(verts)

    # Values clamped in [0, 1]
    assert float(np.min(curv)) >= 0.0 and float(np.max(curv)) <= 1.0
    assert float(np.min(ao)) >= 0.15 and float(np.max(ao)) <= 1.0


def test_bake_high_to_low_pbr_pipeline(
    tmp_path: Path,
    dense_high_poly_relief: Tuple[np.ndarray, np.ndarray],
    low_poly_quad_plane: Tuple[np.ndarray, np.ndarray, np.ndarray],
) -> None:
    """Verify end-to-end texture baking producing valid image maps."""
    high_v, high_n = dense_high_poly_relief
    low_v, low_f, low_uv = low_poly_quad_plane

    cfg = BakeConfig(resolution=256, base_roughness=0.60, base_metallic=0.10)
    baked = bake_high_to_low_pbr(
        high_verts=high_v,
        high_normals=high_n,
        low_verts=low_v,
        low_faces=low_f,
        low_uvs=low_uv,
        output_dir=tmp_path,
        asset_prefix="test_quad",
        config=cfg,
    )

    assert isinstance(baked, BakedPBRMaps)
    assert baked.resolution == 256
    assert baked.bake_time_seconds > 0.0

    # Verify Normal map
    n_file = Path(baked.normal_map_path)
    assert n_file.exists()
    with Image.open(n_file) as n_img:
        assert n_img.size == (256, 256)
        n_arr = np.array(n_img)
        # Dominant color must have strong blue channel (~255) and centered red/green (~128)
        assert np.mean(n_arr[:, :, 2]) > 200
        assert 100 < np.mean(n_arr[:, :, 0]) < 160
        assert 100 < np.mean(n_arr[:, :, 1]) < 160

    # Verify AO map
    ao_file = Path(baked.ao_map_path)
    assert ao_file.exists()
    with Image.open(ao_file) as ao_img:
        assert ao_img.size == (256, 256)

    # Verify Cavity map
    cav_file = Path(baked.cavity_map_path)
    assert cav_file.exists()

    # Verify packed ORM map (Red=AO, Green=Roughness, Blue=Metallic)
    orm_file = Path(baked.orm_map_path)
    assert orm_file.exists()
    with Image.open(orm_file) as orm_img:
        assert orm_img.size == (256, 256)
        orm_arr = np.array(orm_img)
        assert orm_arr.shape == (256, 256, 3)
        # Blue channel should match base_metallic (0.10 * 255 = 25)
        assert np.isclose(float(np.mean(orm_arr[:, :, 2])), 25.0, atol=5.0)
