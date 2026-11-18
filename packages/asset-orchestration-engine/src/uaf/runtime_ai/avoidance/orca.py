"""
UAF-81.82: Optimal Reciprocal Collision Avoidance (ORCA) Deterministic Solver.
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple

from ..models.definition import (
    AgentKinematics,
    Vec3,
    ensure_finite_float,
    ensure_finite_vec3,
    vec3_distance,
    vec3_length,
    vec3_scale,
)


class ORCAHalfPlane:
    """2D Linear half-plane constraint in XZ plane: dot(v - point, normal) >= 0."""
    def __init__(self, point_xz: Tuple[float, float], normal_xz: Tuple[float, float]):
        self.point = point_xz
        self.normal = normal_xz  # Unit normal pointing toward allowed half-plane


class ORCASolver:
    """
    Deterministic ORCA solver for reciprocal multi-agent collision avoidance.
    Guarantees stable, reproducible velocity resolution with a strict 3-tier fallback ladder.
    """

    @staticmethod
    def compute_orca_halfplane(
        pos_a: Vec3,
        vel_a: Vec3,
        radius_a: float,
        pos_b: Vec3,
        vel_b: Vec3,
        radius_b: float,
        time_horizon: float = 2.0,
        time_step: float = 0.1,
    ) -> ORCAHalfPlane:
        """Construct the ORCA half-plane constraint induced by neighbor B on agent A."""
        rel_pos_x = pos_b[0] - pos_a[0]
        rel_pos_z = pos_b[2] - pos_a[2]
        rel_vel_x = vel_a[0] - vel_b[0]
        rel_vel_z = vel_a[2] - vel_b[2]

        dist_sq = rel_pos_x * rel_pos_x + rel_pos_z * rel_pos_z
        combined_radius = radius_a + radius_b
        combined_radius_sq = combined_radius * combined_radius

        inv_time_horizon = 1.0 / max(1e-4, time_horizon)

        if dist_sq > combined_radius_sq:
            # Not in collision yet
            w_x = rel_vel_x - inv_time_horizon * rel_pos_x
            w_z = rel_vel_z - inv_time_horizon * rel_pos_z
            w_len_sq = w_x * w_x + w_z * w_z

            dot_w_p = w_x * rel_pos_x + w_z * rel_pos_z

            if dot_w_p < 0.0 and (dot_w_p * dot_w_p) > (combined_radius_sq * w_len_sq):
                # Project on cut-off circle
                w_len = math.sqrt(max(1e-12, w_len_sq))
                unit_w_x = w_x / w_len
                unit_w_z = w_z / w_len

                normal_x = unit_w_x
                normal_z = unit_w_z
                u_x = (combined_radius * inv_time_horizon - w_len) * unit_w_x
                u_z = (combined_radius * inv_time_horizon - w_len) * unit_w_z
            else:
                # Project on cone legs
                leg_dist = math.sqrt(max(1e-12, dist_sq - combined_radius_sq))
                if (rel_pos_x * w_z - rel_pos_z * w_x) > 0.0:
                    # Left leg
                    normal_x = (rel_pos_x * leg_dist - rel_pos_z * combined_radius) / dist_sq
                    normal_z = (rel_pos_z * leg_dist + rel_pos_x * combined_radius) / dist_sq
                else:
                    # Right leg
                    normal_x = -(rel_pos_x * leg_dist + rel_pos_z * combined_radius) / dist_sq
                    normal_z = -(rel_pos_z * leg_dist - rel_pos_x * combined_radius) / dist_sq

                dot_v_n = rel_vel_x * normal_x + rel_vel_z * normal_z
                u_x = -dot_v_n * normal_x
                u_z = -dot_v_n * normal_z
        else:
            # Overlapping collision: push apart using time_step
            inv_time_step = 1.0 / max(1e-4, time_step)
            w_x = rel_vel_x - inv_time_step * rel_pos_x
            w_z = rel_vel_z - inv_time_step * rel_pos_z
            w_len = math.sqrt(max(1e-12, w_x * w_x + w_z * w_z))
            unit_w_x = w_x / w_len
            unit_w_z = w_z / w_len

            normal_x = unit_w_x
            normal_z = unit_w_z
            u_x = (combined_radius * inv_time_step - w_len) * unit_w_x
            u_z = (combined_radius * inv_time_step - w_len) * unit_w_z

        # Half-plane point: vel_a + 0.5 * u (reciprocal responsibility)
        pt_x = vel_a[0] + 0.5 * u_x
        pt_z = vel_a[2] + 0.5 * u_z

        return ORCAHalfPlane((pt_x, pt_z), (normal_x, normal_z))

    @staticmethod
    def solve_avoidance(
        agent: AgentKinematics,
        neighbors: Sequence[Tuple[str, AgentKinematics]],
        time_horizon: float = 2.0,
        time_step: float = 0.1,
    ) -> Vec3:
        """
        Compute safe velocity for agent taking into account all neighbors.
        Neighbors must be sorted deterministically: (distance ASC, agent_id ASC).
        """
        # Sort neighbors deterministically
        sorted_neighbors = sorted(
            neighbors,
            key=lambda item: (vec3_distance(agent.position, item[1].position), item[0])
        )

        halfplanes: List[ORCAHalfPlane] = []
        for _, n_kin in sorted_neighbors:
            hp = ORCASolver.compute_orca_halfplane(
                agent.position,
                agent.velocity,
                agent.radius,
                n_kin.position,
                n_kin.velocity,
                n_kin.radius,
                time_horizon,
                time_step,
            )
            halfplanes.append(hp)

        pref_x = agent.preferred_velocity[0]
        pref_z = agent.preferred_velocity[2]

        # Tier 1: Check if preferred velocity satisfies all half-planes
        all_satisfied = True
        for hp in halfplanes:
            dx = pref_x - hp.point[0]
            dz = pref_z - hp.point[1]
            if (dx * hp.normal[0] + dz * hp.normal[1]) < -1e-5:
                all_satisfied = False
                break

        if all_satisfied:
            # Clamp to max speed
            speed = math.sqrt(pref_x * pref_x + pref_z * pref_z)
            if speed > agent.max_speed:
                scale = agent.max_speed / speed
                pref_x *= scale
                pref_z *= scale
            return ensure_finite_vec3((pref_x, agent.preferred_velocity[1], pref_z), "ORCA.tier1")

        # Tier 2: Linear Programming in 2D (project onto boundary lines)
        curr_vx = pref_x
        curr_vz = pref_z

        feasible = True
        for i, hp in enumerate(halfplanes):
            dx = curr_vx - hp.point[0]
            dz = curr_vz - hp.point[1]
            if (dx * hp.normal[0] + dz * hp.normal[1]) < 0.0:
                # Project curr_v onto line dot(v - point, normal) = 0
                # Line direction is perpendicular to normal: dir = (-normal_z, normal_x)
                line_dir_x = -hp.normal[1]
                line_dir_z = hp.normal[0]

                # Project point: p_proj = hp.point + proj_t * line_dir
                # Find proj_t that minimizes distance to (pref_x, pref_z)
                diff_pref_x = pref_x - hp.point[0]
                diff_pref_z = pref_z - hp.point[1]
                t = diff_pref_x * line_dir_x + diff_pref_z * line_dir_z

                cand_x = hp.point[0] + t * line_dir_x
                cand_z = hp.point[1] + t * line_dir_z

                # Check previous half-planes for this candidate
                valid_for_prev = True
                for j in range(i):
                    prev_hp = halfplanes[j]
                    pdx = cand_x - prev_hp.point[0]
                    pdz = cand_z - prev_hp.point[1]
                    if (pdx * prev_hp.normal[0] + pdz * prev_hp.normal[1]) < -1e-4:
                        valid_for_prev = False
                        break

                if valid_for_prev:
                    curr_vx = cand_x
                    curr_vz = cand_z
                else:
                    feasible = False
                    break

        if feasible:
            speed = math.sqrt(curr_vx * curr_vx + curr_vz * curr_vz)
            if speed > agent.max_speed:
                scale = agent.max_speed / max(1e-6, speed)
                curr_vx *= scale
                curr_vz *= scale
            return ensure_finite_vec3((curr_vx, agent.preferred_velocity[1], curr_vz), "ORCA.tier2")

        # Tier 3: Least violation velocity fallback (minimizes deepest constraint violation)
        best_vx = 0.0
        best_vz = 0.0
        min_violation = float("inf")

        # Sample 16 deterministic directional candidates
        for angle_deg in range(0, 360, 24):
            rad = math.radians(angle_deg)
            for spd_ratio in (1.0, 0.5, 0.25):
                sample_spd = agent.max_speed * spd_ratio
                sample_vx = sample_spd * math.cos(rad)
                sample_vz = sample_spd * math.sin(rad)

                max_v = 0.0
                for hp in halfplanes:
                    dx = sample_vx - hp.point[0]
                    dz = sample_vz - hp.point[1]
                    penetration = -(dx * hp.normal[0] + dz * hp.normal[1])
                    if penetration > max_v:
                        max_v = penetration

                # Add small preference towards pref_velocity
                dist_to_pref = math.sqrt((sample_vx - pref_x)**2 + (sample_vz - pref_z)**2)
                score = max_v * 10.0 + dist_to_pref

                if score < min_violation:
                    min_violation = score
                    best_vx = sample_vx
                    best_vz = sample_vz

        return ensure_finite_vec3((best_vx, 0.0, best_vz), "ORCA.tier3")
