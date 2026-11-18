import math
import copy
from typing import List, Dict, Any, Optional, Tuple, Callable
from ..core.guardrail_types import SpatialViolationType, RemediationStrategy
from ..core.guardrail_schema import (
    EntitySpatialSpec, SpatialClearanceViolation, SpatialClearanceResult
)

class SpatialClearanceGuard:
    """
    Agnostic guardrail that enforces contact datum and spatial clearance invariants.
    Eliminates entity ground-sinking/floating and prevents entities from overlapping
    or spawning inside each other using non-linear relaxation repulsion.
    """

    def validate_and_resolve(
        self,
        entities: List[EntitySpatialSpec],
        ground_height_sampler: Optional[Callable[[float, float], float]] = None,
        clearance_margin: float = 15.0, # 15 cm safety buffer
        max_repulsion_iterations: int = 40
    ) -> SpatialClearanceResult:
        violations: List[SpatialClearanceViolation] = []
        remediations: List[str] = []

        adjusted_entities = [copy.deepcopy(e) for e in entities]

        # 1. Ground Datum Invariant Check & Auto-Calibration
        for ent in adjusted_entities:
            if ent.is_grounded:
                # Invariant: mesh_bottom_offset_z must equal -capsule_half_height
                expected_offset = -abs(ent.capsule_half_height)
                delta = ent.mesh_bottom_offset_z - expected_offset

                if abs(delta) > 0.1: # Threshold 1 mm
                    vtype = SpatialViolationType.GROUND_PENETRATION if delta < 0 else SpatialViolationType.GROUND_FLOATING
                    violations.append(
                        SpatialClearanceViolation(
                            violation_type=vtype,
                            entity_a_id=ent.entity_id,
                            overlap_distance=abs(delta),
                            message=f"Entity '{ent.entity_id}' datum mismatch: mesh offset Z is {ent.mesh_bottom_offset_z:.1f} cm, expected {expected_offset:.1f} cm relative to capsule base.",
                            suggested_remediation=RemediationStrategy.AUTO_ALIGN_DATUM
                        )
                    )
                    # Auto-Calibrate Datum
                    ent.mesh_bottom_offset_z = expected_offset
                    remediations.append(
                        f"Auto-aligned datum for '{ent.entity_id}': mesh_bottom_offset_z set to {expected_offset:.1f} cm."
                    )

                # Ground Surface Clamping if height sampler provided
                if ground_height_sampler is not None:
                    gx, gy, gz = ent.position
                    surface_z = ground_height_sampler(gx, gy)
                    min_allowed_z = surface_z + ent.capsule_half_height
                    if gz < min_allowed_z - 0.5:
                        sink_depth = min_allowed_z - gz
                        violations.append(
                            SpatialClearanceViolation(
                                violation_type=SpatialViolationType.GROUND_PENETRATION,
                                entity_a_id=ent.entity_id,
                                overlap_distance=sink_depth,
                                message=f"Entity '{ent.entity_id}' is sunk {sink_depth:.1f} cm below ground surface at ({gx:.1f}, {gy:.1f}).",
                                suggested_remediation=RemediationStrategy.AUTO_ALIGN_DATUM
                            )
                        )
                        ent.position = (gx, gy, min_allowed_z)
                        remediations.append(
                            f"Clamped '{ent.entity_id}' Z position from {gz:.1f} to {min_allowed_z:.1f} cm."
                        )

        # 2. Mutual Exclusion Clearance (Entity-Entity Overlap)
        overlap_found = True
        iteration = 0

        while overlap_found and iteration < max_repulsion_iterations:
            overlap_found = False
            iteration += 1

            for i in range(len(adjusted_entities)):
                for j in range(i + 1, len(adjusted_entities)):
                    e1 = adjusted_entities[i]
                    e2 = adjusted_entities[j]

                    dx = e2.position[0] - e1.position[0]
                    dy = e2.position[1] - e1.position[1]
                    dz = abs(e2.position[2] - e1.position[2])

                    dist_xy = math.sqrt(dx * dx + dy * dy)
                    min_dist_xy = e1.capsule_radius + e2.capsule_radius + clearance_margin
                    vertical_overlap = dz < (e1.capsule_half_height + e2.capsule_half_height)

                    if dist_xy < min_dist_xy and vertical_overlap:
                        overlap_found = True
                        penetration = min_dist_xy - dist_xy

                        if iteration == 1:
                            violations.append(
                                SpatialClearanceViolation(
                                    violation_type=SpatialViolationType.ENTITY_OVERLAP,
                                    entity_a_id=e1.entity_id,
                                    entity_b_id=e2.entity_id,
                                    overlap_distance=penetration,
                                    message=f"Overlap detected between '{e1.entity_id}' and '{e2.entity_id}': dist={dist_xy:.1f} cm, required={min_dist_xy:.1f} cm.",
                                    suggested_remediation=RemediationStrategy.REPULSION_DISPERSION
                                )
                            )

                        # Repulsion push along normal
                        if dist_xy < 0.001:
                            # Deterministic separation angle
                            h = (hash(e1.entity_id) ^ hash(e2.entity_id)) % 360
                            rad = math.radians(h)
                            nx, ny = math.cos(rad), math.sin(rad)
                        else:
                            nx, ny = dx / dist_xy, dy / dist_xy

                        push = (penetration * 0.55)
                        e1.position = (e1.position[0] - nx * push, e1.position[1] - ny * push, e1.position[2])
                        e2.position = (e2.position[0] + nx * push, e2.position[1] + ny * push, e2.position[2])

                        # Keep clamped to ground if sampler provided
                        if ground_height_sampler is not None and e1.is_grounded:
                            e1.position = (e1.position[0], e1.position[1], ground_height_sampler(e1.position[0], e1.position[1]) + e1.capsule_half_height)
                        if ground_height_sampler is not None and e2.is_grounded:
                            e2.position = (e2.position[0], e2.position[1], ground_height_sampler(e2.position[0], e2.position[1]) + e2.capsule_half_height)

        if iteration > 1:
            remediations.append(
                f"Resolved entity overlaps via repulsion solver in {iteration} iterations."
            )

        is_valid = (len(violations) == 0)

        return SpatialClearanceResult(
            is_valid=is_valid,
            violations=violations,
            adjusted_entities=adjusted_entities,
            remediations_applied=remediations
        )
