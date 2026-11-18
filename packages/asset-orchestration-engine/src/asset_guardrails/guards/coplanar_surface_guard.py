import math
import copy
from typing import List, Dict, Any, Optional, Tuple
from ..core.guardrail_types import CoplanarConflictType, RemediationStrategy
from ..core.guardrail_schema import (
    SurfacePlaneSpec, CoplanarConflict, CoplanarRemediationResult
)

class CoplanarSurfaceGuard:
    """
    Agnostic guardrail that detects and resolves coplanar surface collisions and Z-fighting.
    Provides automated micro-layering depth offsets and coincident face culling
    for modular tiles, floors, walls, and structural props.
    """

    def validate_and_resolve(
        self,
        surfaces: List[SurfacePlaneSpec],
        plane_tolerance: float = 0.01, # 0.1 mm tolerance for coplanarity
        micro_offset_step: float = 0.05, # 0.5 mm micro-displacement
        cull_internal_faces: bool = True
    ) -> CoplanarRemediationResult:
        conflicts: List[CoplanarConflict] = []
        remediations: List[str] = []
        faces_culled = 0
        micro_offsets_applied = 0

        adjusted = [copy.deepcopy(s) for s in surfaces]

        for i in range(len(adjusted)):
            for j in range(i + 1, len(adjusted)):
                s1 = adjusted[i]
                s2 = adjusted[j]

                if s1.is_culled or s2.is_culled:
                    continue

                dot = self._dot3(s1.normal, s2.normal)
                is_parallel = abs(dot - 1.0) < 0.001
                is_anti_parallel = abs(dot + 1.0) < 0.001

                if not (is_parallel or is_anti_parallel):
                    continue

                # Distance delta
                if is_parallel:
                    dist_delta = abs(s1.distance - s2.distance)
                else:
                    dist_delta = abs(s1.distance + s2.distance)

                if dist_delta > plane_tolerance:
                    continue

                # Check 2D bounding overlap
                if not self._check_vertex_overlap(s1.vertices, s2.vertices):
                    continue

                # Conflict confirmed!
                if is_anti_parallel and cull_internal_faces:
                    # Abutting internal face between solid blocks
                    conflicts.append(
                        CoplanarConflict(
                            conflict_type=CoplanarConflictType.COINCIDENT_INTERNAL_FACE,
                            surface_a_id=s1.surface_id,
                            surface_b_id=s2.surface_id,
                            normal_dot=dot,
                            distance_delta=dist_delta,
                            message=f"Coincident back-to-back internal face detected between '{s1.surface_id}' and '{s2.surface_id}'.",
                            suggested_remediation=RemediationStrategy.COINCIDENT_FACE_CULL
                        )
                    )
                    # Cull both redundant interior faces
                    s1.is_culled = True
                    s2.is_culled = True
                    faces_culled += 2
                    remediations.append(
                        f"Culled redundant interior faces '{s1.surface_id}' and '{s2.surface_id}'."
                    )
                else:
                    # Same-facing coplanar overlap -> High Z-fighting risk!
                    conflicts.append(
                        CoplanarConflict(
                            conflict_type=CoplanarConflictType.IDENTICAL_PLANE_OVERLAP,
                            surface_a_id=s1.surface_id,
                            surface_b_id=s2.surface_id,
                            normal_dot=dot,
                            distance_delta=dist_delta,
                            message=f"Coplanar Z-fighting hazard between '{s1.surface_id}' and '{s2.surface_id}' (delta={dist_delta:.4f}).",
                            suggested_remediation=RemediationStrategy.MICRO_LAYERING_OFFSET
                        )
                    )
                    # Apply micro-layering offset along normal
                    offset = micro_offset_step * (1 + micro_offsets_applied)
                    s2.distance += offset
                    s2.vertices = [
                        (v[0] + s2.normal[0] * offset, v[1] + s2.normal[1] * offset, v[2] + s2.normal[2] * offset)
                        for v in s2.vertices
                    ]
                    micro_offsets_applied += 1
                    remediations.append(
                        f"Applied micro-layering offset +{offset:.3f} to surface '{s2.surface_id}' along normal."
                    )

        is_valid = (len(conflicts) == 0)

        return CoplanarRemediationResult(
            is_valid=is_valid,
            conflicts=conflicts,
            adjusted_surfaces=adjusted,
            faces_culled=faces_culled,
            micro_offsets_applied=micro_offsets_applied,
            remediations_applied=remediations
        )

    def _dot3(self, a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    def _check_vertex_overlap(self, v1: List[Tuple[float, float, float]], v2: List[Tuple[float, float, float]]) -> bool:
        if not v1 or not v2:
            return True # Fallback: assume potential overlap

        # Compute 3D AABB for both vertex clouds
        min1 = [min(v[c] for v in v1) for c in range(3)]
        max1 = [max(v[c] for v in v1) for c in range(3)]
        min2 = [min(v[c] for v in v2) for c in range(3)]
        max2 = [max(v[c] for v in v2) for c in range(3)]

        # Check AABB intersection with small margin
        margin = 0.001
        overlap_x = (min1[0] <= max2[0] + margin) and (max1[0] >= min2[0] - margin)
        overlap_y = (min1[1] <= max2[1] + margin) and (max1[1] >= min2[1] - margin)
        overlap_z = (min1[2] <= max2[2] + margin) and (max1[2] >= min2[2] - margin)

        return overlap_x and overlap_y and overlap_z

    @staticmethod
    def snap_modular_tiles(
        tile_positions: List[Tuple[float, float, float]],
        tile_size: float = 100.0,
        tolerance: float = 1.0
    ) -> List[Tuple[float, float, float]]:
        """
        Enforces strict modular grid alignment to eliminate sub-millimeter fractional seams.
        """
        snapped: List[Tuple[float, float, float]] = []
        for p in tile_positions:
            sx = round(p[0] / tile_size) * tile_size
            sy = round(p[1] / tile_size) * tile_size
            sz = round(p[2] / tile_size) * tile_size
            snapped.append((sx, sy, sz))
        return snapped
