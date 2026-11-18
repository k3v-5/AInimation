"""
UAF-81.89.2: Skeletal Mesh Surface Sampler and Animation Coupler.
Samples particles uniformly on animated character surfaces with Linear Blend Skinning and bone velocity inheritance.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Dict, Optional
from ..core.contracts import (
    SkeletalVertex,
    SkeletalBoneTransform,
    ensure_finite_vec3,
    clamp_scalar,
)


class SkeletalMeshSampler:
    """
    Uniform surface sampler for animated skeletal meshes.
    Computes deformed positions, surface normals, and inherited velocities on active meshes.
    """

    def __init__(
        self,
        vertices: List[SkeletalVertex],
        triangles: List[Tuple[int, int, int]],
        bones: Optional[Dict[str, SkeletalBoneTransform]] = None,
    ) -> None:
        self.vertices: List[SkeletalVertex] = vertices
        self.triangles: List[Tuple[int, int, int]] = triangles
        self.bones: Dict[str, SkeletalBoneTransform] = bones or {}
        self.bone_list: List[SkeletalBoneTransform] = sorted(self.bones.values(), key=lambda b: b.bone_index)

        self._triangle_areas: List[float] = []
        self._area_cdf: List[float] = []
        self._total_surface_area: float = 0.0
        self._rebuild_surface_cdf()

    def set_bones(self, bones: Dict[str, SkeletalBoneTransform]) -> None:
        self.bones = bones
        self.bone_list = sorted(self.bones.values(), key=lambda b: b.bone_index)

    def _rebuild_surface_cdf(self) -> None:
        """Precomputes Cumulative Distribution Function of triangle areas for uniform surface picking."""
        self._triangle_areas.clear()
        self._area_cdf.clear()
        accum = 0.0

        for idx0, idx1, idx2 in self.triangles:
            v0 = self.vertices[idx0].position
            v1 = self.vertices[idx1].position
            v2 = self.vertices[idx2].position

            # Edge vectors
            e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
            e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])

            # Cross product
            cx = e1[1] * e2[2] - e1[2] * e2[1]
            cy = e1[2] * e2[0] - e1[0] * e2[2]
            cz = e1[0] * e2[1] - e1[1] * e2[0]

            area = 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)
            self._triangle_areas.append(area)
            accum += area
            self._area_cdf.append(accum)

        self._total_surface_area = accum
        # Normalize CDF to [0, 1]
        if self._total_surface_area > 0.0:
            self._area_cdf = [val / self._total_surface_area for val in self._area_cdf]

    def _deform_vertex(self, vert: SkeletalVertex) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Computes deformed position and inherited velocity using Linear Blend Skinning (LBS).
        """
        if not self.bone_list:
            return vert.position, (0.0, 0.0, 0.0)

        pos_x, pos_y, pos_z = 0.0, 0.0, 0.0
        vel_x, vel_y, vel_z = 0.0, 0.0, 0.0

        for i in range(4):
            b_idx = vert.bone_indices[i]
            weight = vert.bone_weights[i]
            if weight <= 0.0001 or b_idx >= len(self.bone_list):
                continue

            bone = self.bone_list[b_idx]
            bp = bone.position
            bv = bone.linear_velocity
            bw = bone.angular_velocity

            # Transform vertex position with bone translation
            rx = vert.position[0]
            ry = vert.position[1]
            rz = vert.position[2]

            pos_x += weight * (bp[0] + rx)
            pos_y += weight * (bp[1] + ry)
            pos_z += weight * (bp[2] + rz)

            # Tangential velocity: v_linear + (omega x r)
            tang_x = bw[1] * rz - bw[2] * ry
            tang_y = bw[2] * rx - bw[0] * rz
            tang_z = bw[0] * ry - bw[1] * rx

            vel_x += weight * (bv[0] + tang_x)
            vel_y += weight * (bv[1] + tang_y)
            vel_z += weight * (bv[2] + tang_z)

        return (pos_x, pos_y, pos_z), (vel_x, vel_y, vel_z)

    def sample_surface_point(
        self,
        rng_tri: float,
        rng_u: float,
        rng_v: float,
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Samples a random point uniformly on the deformed skeletal mesh.
        Returns (position, normal, inherited_velocity).
        """
        if not self.triangles or not self._area_cdf:
            return (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0)

        # 1. Binary search CDF for triangle index
        target = clamp_scalar(rng_tri, 0.0, 0.999999)
        low, high = 0, len(self._area_cdf) - 1
        tri_idx = high
        while low <= high:
            mid = (low + high) // 2
            if self._area_cdf[mid] >= target:
                tri_idx = mid
                high = mid - 1
            else:
                low = mid + 1

        idx0, idx1, idx2 = self.triangles[tri_idx]
        v0 = self.vertices[idx0]
        v1 = self.vertices[idx1]
        v2 = self.vertices[idx2]

        # 2. Random barycentric coordinates on picked triangle
        u = rng_u
        v = rng_v
        if u + v > 1.0:
            u = 1.0 - u
            v = 1.0 - v
        w = 1.0 - u - v

        # 3. Deform the 3 vertices
        p0, vel0 = self._deform_vertex(v0)
        p1, vel1 = self._deform_vertex(v1)
        p2, vel2 = self._deform_vertex(v2)

        # 4. Interpolate position and velocity
        pos = (
            w * p0[0] + u * p1[0] + v * p2[0],
            w * p0[1] + u * p1[1] + v * p2[1],
            w * p0[2] + u * p1[2] + v * p2[2],
        )
        vel = (
            w * vel0[0] + u * vel1[0] + v * vel2[0],
            w * vel0[1] + u * vel1[1] + v * vel2[1],
            w * vel0[2] + u * vel1[2] + v * vel2[2],
        )

        # 5. Normal calculation
        e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        n_len = math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-6
        norm = (nx / n_len, ny / n_len, nz / n_len)

        return ensure_finite_vec3(pos), ensure_finite_vec3(norm), ensure_finite_vec3(vel)

    def sample_socket(
        self,
        bone_name: str,
        local_offset: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Samples the world position and velocity of a named bone/socket with local offset."""
        if bone_name in self.bones:
            bone = self.bones[bone_name]
            pos = (
                bone.position[0] + local_offset[0],
                bone.position[1] + local_offset[1],
                bone.position[2] + local_offset[2],
            )
            vel = bone.linear_velocity
            return ensure_finite_vec3(pos), ensure_finite_vec3(vel)
        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
