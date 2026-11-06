"""
Studio PBR High-to-Low Poly Texture Baker for IANIMATION.

Projects high-frequency geometric micro-details (wrinkles, panel seams, pores, cloth weave)
from dense neural sculpts onto retopologized low-poly quad meshes.

Generates:
1. Tangent-Space Normal Maps (RGB: 128, 128, 255 base) with Gram-Schmidt orthogonalized TBN.
2. Ambient Occlusion (AO) via local hemisphere / distance occlusion.
3. Curvature / Cavity Maps for edge wear and contact shadows.
4. glTF-compliant packed ORM (Occlusion, Roughness, Metallic) texture maps.

100% Zero-Any compliant with strict typing, NumPy vectorization, and SciPy cKDTree.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field
from scipy.spatial import cKDTree

logger = logging.getLogger("ianimation.ai.pbr_baker")


class BakeConfig(BaseModel):
    """Configuration parameters for PBR texture baking."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    resolution: int = Field(default=1024, ge=256, le=4096)
    ray_max_distance: float = Field(default=0.15, gt=0.0)
    base_roughness: float = Field(default=0.55, ge=0.0, le=1.0)
    base_metallic: float = Field(default=0.0, ge=0.0, le=1.0)
    invert_green_channel: bool = Field(default=False)  # DirectX vs OpenGL normal map standard


class BakedPBRMaps(BaseModel):
    """File paths and metadata for baked PBR texture assets."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    normal_map_path: str
    ao_map_path: str
    cavity_map_path: str
    orm_map_path: str
    resolution: int
    bake_time_seconds: float


def compute_mesh_tangents(
    vertices: NDArray[np.float32],
    faces: NDArray[np.int32],
    uvs: NDArray[np.float32],
) -> Tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.float32]]:
    """
    Compute orthogonal Tangent, Bitangent, and Normal (TBN) frames for each vertex
    conforming to the MikkTSpace convention.
    """
    n_v = len(vertices)
    tangents = np.zeros((n_v, 3), dtype=np.float32)
    bitangents = np.zeros((n_v, 3), dtype=np.float32)
    normals = np.zeros((n_v, 3), dtype=np.float32)

    # Convert quads to triangles if needed
    if faces.shape[1] == 4:
        tris = np.vstack([
            faces[:, [0, 1, 2]],
            faces[:, [0, 2, 3]],
        ])
    else:
        tris = faces

    v0 = vertices[tris[:, 0]]
    v1 = vertices[tris[:, 1]]
    v2 = vertices[tris[:, 2]]

    uv0 = uvs[tris[:, 0]]
    uv1 = uvs[tris[:, 1]]
    uv2 = uvs[tris[:, 2]]

    e1 = v1 - v0
    e2 = v2 - v0
    duv1 = uv1 - uv0
    duv2 = uv2 - uv0

    # Face normals
    fn = np.cross(e1, e2)
    np.add.at(normals, tris[:, 0], fn)
    np.add.at(normals, tris[:, 1], fn)
    np.add.at(normals, tris[:, 2], fn)

    # Det for UV inversion
    det = duv1[:, 0] * duv2[:, 1] - duv1[:, 1] * duv2[:, 0]
    valid_det = np.abs(det) > 1e-8
    inv_det = np.where(valid_det, 1.0 / np.where(valid_det, det, 1.0), 0.0)[:, None]

    tri_tangents = (e1 * duv2[:, 1:2] - e2 * duv1[:, 1:2]) * inv_det
    tri_bitangents = (e2 * duv1[:, 0:1] - e1 * duv2[:, 0:1]) * inv_det

    np.add.at(tangents, tris[:, 0], tri_tangents)
    np.add.at(tangents, tris[:, 1], tri_tangents)
    np.add.at(tangents, tris[:, 2], tri_tangents)

    np.add.at(bitangents, tris[:, 0], tri_bitangents)
    np.add.at(bitangents, tris[:, 1], tri_bitangents)
    np.add.at(bitangents, tris[:, 2], tri_bitangents)

    # Normalize normals
    n_lens = np.maximum(1e-8, np.linalg.norm(normals, axis=1, keepdims=True))
    normals = normals / n_lens

    # Gram-Schmidt Orthogonalization: T' = normalize(T - (N · T) * N)
    dot_nt = np.sum(normals * tangents, axis=1, keepdims=True)
    tangents_ortho = tangents - dot_nt * normals
    t_lens = np.maximum(1e-8, np.linalg.norm(tangents_ortho, axis=1, keepdims=True))
    tangents = tangents_ortho / t_lens

    # B = normalize(cross(N, T))
    cross_b = np.cross(normals, tangents)
    b_sign = np.sign(np.sum(cross_b * bitangents, axis=1, keepdims=True))
    b_sign = np.where(b_sign == 0.0, 1.0, b_sign)
    bitangents = cross_b * b_sign

    return (
        tangents.astype(np.float32),
        bitangents.astype(np.float32),
        normals.astype(np.float32),
    )


def compute_surface_curvature_and_ao(
    high_verts: NDArray[np.float32],
    high_normals: NDArray[np.float32],
    k_neighbors: int = 16,
) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
    """
    Compute local mean curvature and ambient occlusion factors on dense high-poly vertices.
    """
    n_v = len(high_verts)
    tree = cKDTree(high_verts)
    k = min(k_neighbors, max(2, n_v))
    dists, indices = tree.query(high_verts, k=k)

    # Vector from center to neighbor vertices
    nb_verts = high_verts[indices]  # (N, k, 3)
    diff = nb_verts - high_verts[:, None, :]  # (N, k, 3)

    # Projection along normal: positive = concave (crevice), negative = convex (ridge)
    normal_proj = np.sum(diff * high_normals[:, None, :], axis=2)  # (N, k)

    # Mean curvature: average normal deflection
    curvature = np.mean(normal_proj, axis=1)  # (N,)

    # Normalize curvature to [0, 1] (0.5 = flat, 0.0 = deep crease, 1.0 = sharp ridge)
    curv_std = float(np.std(curvature))
    scale = max(1e-5, curv_std * 2.5)
    curv_norm = np.clip(0.5 + curvature / (2.0 * scale), 0.0, 1.0).astype(np.float32)

    # Ambient occlusion: local depth self-occlusion
    ao = np.clip(1.0 - np.maximum(0.0, -curvature / scale), 0.15, 1.0).astype(np.float32)

    return curv_norm, ao


def bake_high_to_low_pbr(
    high_verts: NDArray[np.float32],
    high_normals: NDArray[np.float32],
    low_verts: NDArray[np.float32],
    low_faces: NDArray[np.int32],
    low_uvs: NDArray[np.float32],
    output_dir: Union[str, Path],
    asset_prefix: str = "character",
    config: Optional[BakeConfig] = None,
) -> BakedPBRMaps:
    """
    Execute high-performance PBR texture baking.
    Produces Tangent-Space Normal Map, Ambient Occlusion, Cavity, and glTF ORM maps.
    """
    start_time = time.time()
    cfg = config or BakeConfig()
    res = cfg.resolution
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    high_v = np.asarray(high_verts, dtype=np.float32)
    high_n = np.asarray(high_normals, dtype=np.float32)
    low_v = np.asarray(low_verts, dtype=np.float32)
    low_f = np.asarray(low_faces, dtype=np.int32)
    low_uv = np.asarray(low_uvs, dtype=np.float32)

    # 1. Compute TBN frame on low-poly mesh
    low_tangents, low_bitangents, low_normals = compute_mesh_tangents(low_v, low_f, low_uv)

    # 2. Compute high-poly curvature & AO
    high_curv, high_ao = compute_surface_curvature_and_ao(high_v, high_n)

    # 3. Spatial KD-Tree of high-poly sculpt
    high_tree = cKDTree(high_v)

    # Sample low-poly vertices against high-poly surface
    dists, near_idx = high_tree.query(low_v, k=1)
    sampled_high_n = high_n[near_idx]
    sampled_high_curv = high_curv[near_idx]
    sampled_high_ao = high_ao[near_idx]

    # Project sampled high normals into low-poly tangent frames:
    # N_tangent = (N_high · T, N_high · B, N_high · N)
    nt_x = np.sum(sampled_high_n * low_tangents, axis=1)
    nt_y = np.sum(sampled_high_n * low_bitangents, axis=1)
    nt_z = np.sum(sampled_high_n * low_normals, axis=1)

    t_norm = np.stack([nt_x, nt_y, nt_z], axis=1)
    t_lens = np.maximum(1e-8, np.linalg.norm(t_norm, axis=1, keepdims=True))
    t_norm = t_norm / t_lens

    if cfg.invert_green_channel:
        t_norm[:, 1] = -t_norm[:, 1]

    # Convert to RGB [0, 255]
    vert_normal_colors = ((t_norm * 0.5 + 0.5) * 255.0).clip(0, 255).astype(np.uint8)
    vert_ao_colors = (sampled_high_ao * 255.0).clip(0, 255).astype(np.uint8)
    vert_curv_colors = (sampled_high_curv * 255.0).clip(0, 255).astype(np.uint8)

    # 4. Rasterize onto UV grid
    normal_img = np.full((res, res, 3), [128, 128, 255], dtype=np.uint8)
    ao_img = np.full((res, res), 255, dtype=np.uint8)
    cavity_img = np.full((res, res), 128, dtype=np.uint8)

    # Map vertex UVs to image pixel coordinates (OpenGL convention: V=0 at bottom)
    px = np.clip((low_uv[:, 0] * (res - 1)).astype(np.int32), 0, res - 1)
    py = np.clip(((1.0 - low_uv[:, 1]) * (res - 1)).astype(np.int32), 0, res - 1)

    # Convert faces to triangle triplets for rasterization
    if low_f.shape[1] == 4:
        raster_tris = np.vstack([low_f[:, [0, 1, 2]], low_f[:, [0, 2, 3]]])
    else:
        raster_tris = low_f

    # Efficient barycentric UV rasterizer for triangles
    for tri in raster_tris:
        i0, i1, i2 = tri[0], tri[1], tri[2]
        x0, y0 = px[i0], py[i0]
        x1, y1 = px[i1], py[i1]
        x2, y2 = px[i2], py[i2]

        min_x = max(0, min(x0, x1, x2))
        max_x = min(res - 1, max(x0, x1, x2))
        min_y = max(0, min(y0, y1, y2))
        max_y = min(res - 1, max(y0, y1, y2))

        if min_x > max_x or min_y > max_y:
            continue

        denom = float((y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2))
        if abs(denom) < 1e-5:
            continue
        inv_denom = 1.0 / denom

        grid_x, grid_y = np.meshgrid(np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1))
        w0 = ((y1 - y2) * (grid_x - x2) + (x2 - x1) * (grid_y - y2)) * inv_denom
        w1 = ((y2 - y0) * (grid_x - x2) + (x0 - x2) * (grid_y - y2)) * inv_denom
        w2 = 1.0 - w0 - w1

        inside = (w0 >= -0.01) & (w1 >= -0.01) & (w2 >= -0.01)
        if not np.any(inside):
            continue

        ix = grid_x[inside]
        iy = grid_y[inside]
        b0 = w0[inside, None]
        b1 = w1[inside, None]
        b2 = w2[inside, None]

        # 3D surface point on low-poly mesh for each UV texel
        p_surf = b0 * low_v[i0] + b1 * low_v[i1] + b2 * low_v[i2]

        # Query nearest high-poly sculpt point for this texel
        _, p_near = high_tree.query(p_surf, k=1)
        high_n_pixel = high_n[p_near]
        high_ao_pixel = high_ao[p_near]
        high_curv_pixel = high_curv[p_near]

        # Interpolated low-poly TBN frame at texel
        t_pixel = b0 * low_tangents[i0] + b1 * low_tangents[i1] + b2 * low_tangents[i2]
        b_pixel = b0 * low_bitangents[i0] + b1 * low_bitangents[i1] + b2 * low_bitangents[i2]
        n_pixel = b0 * low_normals[i0] + b1 * low_normals[i1] + b2 * low_normals[i2]

        # Project high normal into pixel TBN
        nx = np.sum(high_n_pixel * t_pixel, axis=1)
        ny = np.sum(high_n_pixel * b_pixel, axis=1)
        nz = np.sum(high_n_pixel * n_pixel, axis=1)
        if cfg.invert_green_channel:
            ny = -ny

        tangent_frame = np.stack([nx, ny, nz], axis=1)
        tf_lens = np.maximum(1e-8, np.linalg.norm(tangent_frame, axis=1, keepdims=True))
        norm_encoded = ((tangent_frame / tf_lens) * 0.5 + 0.5) * 255.0

        normal_img[iy, ix] = np.clip(norm_encoded, 0, 255).astype(np.uint8)
        ao_img[iy, ix] = np.clip(high_ao_pixel * 255.0, 0, 255).astype(np.uint8)
        cavity_img[iy, ix] = np.clip(high_curv_pixel * 255.0, 0, 255).astype(np.uint8)

    # 5. Pack Khronos glTF standard ORM map (Red = Occlusion, Green = Roughness, Blue = Metallic)
    roughness_val = int(cfg.base_roughness * 255)
    metallic_val = int(cfg.base_metallic * 255)

    # Modulate roughness by cavity map for micro-specularity variations
    roughness_channel = np.clip(
        roughness_val + (128 - cavity_img.astype(np.int16)) // 4,
        0,
        255,
    ).astype(np.uint8)

    orm_img = np.stack(
        [
            ao_img,                                    # R = Ambient Occlusion
            roughness_channel,                         # G = Roughness
            np.full((res, res), metallic_val, dtype=np.uint8),  # B = Metallic
        ],
        axis=-1,
    )

    # 6. Save image files
    normal_path = out_dir / f"{asset_prefix}_pbr_normal.png"
    ao_path = out_dir / f"{asset_prefix}_pbr_ao.png"
    cavity_path = out_dir / f"{asset_prefix}_pbr_cavity.png"
    orm_path = out_dir / f"{asset_prefix}_pbr_orm.png"

    Image.fromarray(normal_img).save(normal_path)
    Image.fromarray(ao_img).save(ao_path)
    Image.fromarray(cavity_img).save(cavity_path)
    Image.fromarray(orm_img).save(orm_path)

    elapsed = round(max(0.01, time.time() - start_time), 3)
    logger.info("PBR texture baking finished in %.2fs: %s (%dx%d)", elapsed, normal_path.name, res, res)

    return BakedPBRMaps(
        normal_map_path=str(normal_path),
        ao_map_path=str(ao_path),
        cavity_map_path=str(cavity_path),
        orm_map_path=str(orm_path),
        resolution=res,
        bake_time_seconds=elapsed,
    )
