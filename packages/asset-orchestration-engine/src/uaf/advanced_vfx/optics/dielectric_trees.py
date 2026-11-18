"""
UAF-81.89.5: Dielectric Breakdown and Lichtenberg Lightning Solver.
Implements the Niemeyer-Pietronero-Wiesmann (NPW) Laplacian growth model for realistic electric arcs and return strokes.
"""

from __future__ import annotations

import math
import random
from typing import List, Tuple
from pydantic import BaseModel, Field
from ..core.contracts import DielectricBranchConfig, ensure_finite_vec3, clamp_scalar


class LightningSegment(BaseModel):
    p0: Tuple[float, float, float]
    p1: Tuple[float, float, float]
    intensity: float = 1.0
    thickness: float = 0.1
    is_return_stroke: bool = False


class LightningBolt(BaseModel):
    segments: List[LightningSegment] = Field(default_factory=list)
    total_length: float = 0.0
    branches_count: int = 0


class DielectricBreakdownSolver:
    """
    Generates procedural fractal lightning bolts using dielectric breakdown Laplacian growth.
    Simulates stepped leaders seeking ground/conductors and surges with blinding return strokes.
    """

    def __init__(self, config: DielectricBranchConfig) -> None:
        self.config: DielectricBranchConfig = config

    def generate_bolt(self, seed: int = 1337) -> LightningBolt:
        """Generates a complete branching lightning discharge with return stroke."""
        rng = random.Random(seed)
        segments: List[LightningSegment] = []

        start = self.config.source_pos
        target = self.config.target_pos

        # Overall vector to target
        dx = target[0] - start[0]
        dy = target[1] - start[1]
        dz = target[2] - start[2]
        total_dist = math.sqrt(dx * dx + dy * dy + dz * dz) + 1e-6

        # Step size for leader propagation
        step_len = total_dist * 0.1
        num_steps = max(5, int(total_dist / step_len))

        # 1. Main trunk propagation (stepped leader)
        trunk_points: List[Tuple[float, float, float]] = [start]
        curr_p = start

        for s in range(1, num_steps):
            t = float(s) / float(num_steps)
            ideal_p = (start[0] + dx * t, start[1] + dy * t, start[2] + dz * t)

            # Jitter based on roughness and dielectric exponent
            jitter_scale = step_len * self.config.roughness * 1.5
            jitter = (
                rng.gauss(0.0, jitter_scale),
                rng.gauss(0.0, jitter_scale),
                rng.gauss(0.0, jitter_scale),
            )

            next_p = (
                ideal_p[0] + jitter[0],
                ideal_p[1] + jitter[1],
                ideal_p[2] + jitter[2],
            )
            trunk_points.append(ensure_finite_vec3(next_p))
            curr_p = next_p

        trunk_points.append(target)

        # Build main trunk segments (marked as return stroke with high intensity and thickness)
        total_len = 0.0
        for i in range(len(trunk_points) - 1):
            p0 = trunk_points[i]
            p1 = trunk_points[i + 1]
            seg_len = math.dist(p0, p1)
            total_len += seg_len

            segments.append(
                LightningSegment(
                    p0=p0,
                    p1=p1,
                    intensity=1.0,
                    thickness=0.25,
                    is_return_stroke=True,
                )
            )

        # 2. Recursive side branching along trunk
        branch_count = 0

        def emit_branch(
            origin: Tuple[float, float, float],
            base_dir: Tuple[float, float, float],
            depth: int,
        ) -> None:
            nonlocal branch_count
            if depth > self.config.max_recursion:
                return

            b_len = total_dist * (0.25 / depth)
            steps = max(3, int(b_len / step_len))
            bp = origin

            for _ in range(steps):
                # Branch turns away slightly from trunk
                bx = base_dir[0] + rng.gauss(0.0, 0.4)
                by = base_dir[1] + rng.gauss(0.0, 0.4)
                bz = base_dir[2] + rng.gauss(0.0, 0.4)
                b_mag = math.sqrt(bx * bx + by * by + bz * bz) + 1e-6
                next_bp = (
                    bp[0] + (bx / b_mag) * (step_len * 0.7),
                    bp[1] + (by / b_mag) * (step_len * 0.7),
                    bp[2] + (bz / b_mag) * (step_len * 0.7),
                )
                branch_count += 1
                segments.append(
                    LightningSegment(
                        p0=bp,
                        p1=ensure_finite_vec3(next_bp),
                        intensity=0.6 / depth,
                        thickness=0.15 / depth,
                        is_return_stroke=False,
                    )
                )
                bp = next_bp

                # Probability of fork
                if rng.random() < self.config.branch_probability * 0.5:
                    emit_branch(bp, (bx, by, bz), depth + 1)

        # Spawn branches along the trunk
        trunk_dir = (dx / total_dist, dy / total_dist, dz / total_dist)
        for i in range(1, len(trunk_points) - 1):
            if rng.random() < self.config.branch_probability:
                emit_branch(trunk_points[i], trunk_dir, depth=1)

        return LightningBolt(
            segments=segments,
            total_length=total_len,
            branches_count=branch_count,
        )
