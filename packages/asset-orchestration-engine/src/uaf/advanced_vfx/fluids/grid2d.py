"""
UAF-81.89.1: 2D Eulerian Incompressible Navier-Stokes Fluid Grid.
Implements Staggered MAC Grid, MacCormack/Semi-Lagrangian Advection, and Jacobi Poisson Pressure Solver.
"""

from __future__ import annotations

import math
from typing import List, Tuple
from ..core.contracts import (
    GridDimensions2D,
    FluidBoundaryCondition,
    AdvectionScheme,
    clamp_scalar,
    ensure_finite_scalar,
)


class EulerianFluidGrid2D:
    """
    2D Staggered Marker-and-Cell (MAC) grid for incompressible fluid dynamics.
    - u-velocity at vertical cell faces (width + 1) * height
    - v-velocity at horizontal cell faces width * (height + 1)
    - scalars (density, pressure, divergence) at cell centers width * height
    """

    def __init__(self, dims: GridDimensions2D, scheme: AdvectionScheme = AdvectionScheme.MACCORMACK_BFECC) -> None:
        self.w: int = dims.width
        self.h: int = dims.height
        self.dx: float = dims.cell_size
        self.scheme: AdvectionScheme = scheme

        # Face velocities
        self.u: List[float] = [0.0] * ((self.w + 1) * self.h)
        self.v: List[float] = [0.0] * (self.w * (self.h + 1))
        self.u_prev: List[float] = [0.0] * ((self.w + 1) * self.h)
        self.v_prev: List[float] = [0.0] * (self.w * (self.h + 1))

        # Cell-centered scalars
        self.density: List[float] = [0.0] * (self.w * self.h)
        self.density_prev: List[float] = [0.0] * (self.w * self.h)
        self.pressure: List[float] = [0.0] * (self.w * self.h)
        self.divergence: List[float] = [0.0] * (self.w * self.h)

        # Solid obstacle mask (True = solid / obstacle cell)
        self.solid: List[bool] = [False] * (self.w * self.h)

    # -----------------------------------------------------------------------
    # Indexing Helpers
    # -----------------------------------------------------------------------
    def _c_idx(self, x: int, y: int) -> int:
        return y * self.w + x

    def _u_idx(self, x: int, y: int) -> int:
        return y * (self.w + 1) + x

    def _v_idx(self, x: int, y: int) -> int:
        return y * self.w + x

    # -----------------------------------------------------------------------
    # Injections
    # -----------------------------------------------------------------------
    def add_density(self, x: int, y: int, amount: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h and not self.solid[self._c_idx(x, y)]:
            idx = self._c_idx(x, y)
            self.density[idx] = max(0.0, self.density[idx] + amount)

    def add_velocity(self, x: int, y: int, vx: float, vy: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            # Add to left/right faces for u
            self.u[self._u_idx(x, y)] += vx * 0.5
            self.u[self._u_idx(x + 1, y)] += vx * 0.5
            # Add to bottom/top faces for v
            self.v[self._v_idx(x, y)] += vy * 0.5
            self.v[self._v_idx(x, y + 1)] += vy * 0.5

    def set_solid(self, x: int, y: int, is_solid: bool) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.solid[self._c_idx(x, y)] = is_solid
            if is_solid:
                self.density[self._c_idx(x, y)] = 0.0

    # -----------------------------------------------------------------------
    # Interpolation
    # -----------------------------------------------------------------------
    def sample_density_bilinear(self, px: float, py: float) -> float:
        """Sample density at continuous grid-space coordinate (px, py)."""
        x = clamp_scalar(px - 0.5, 0.0, float(self.w - 1))
        y = clamp_scalar(py - 0.5, 0.0, float(self.h - 1))

        x0, y0 = int(x), int(y)
        x1 = min(x0 + 1, self.w - 1)
        y1 = min(y0 + 1, self.h - 1)

        fx, fy = x - x0, y - y0

        d00 = self.density[self._c_idx(x0, y0)]
        d10 = self.density[self._c_idx(x1, y0)]
        d01 = self.density[self._c_idx(x0, y1)]
        d11 = self.density[self._c_idx(x1, y1)]

        return (d00 * (1.0 - fx) + d10 * fx) * (1.0 - fy) + (d01 * (1.0 - fx) + d11 * fx) * fy

    def sample_velocity_at(self, px: float, py: float) -> Tuple[float, float]:
        """Sample continuous (u, v) velocity vector at continuous coordinate (px, py)."""
        # u is defined at (i, j + 0.5)
        ux = clamp_scalar(px, 0.0, float(self.w))
        uy = clamp_scalar(py - 0.5, 0.0, float(self.h - 1))
        ux0, uy0 = int(ux), int(uy)
        ux1 = min(ux0 + 1, self.w)
        uy1 = min(uy0 + 1, self.h - 1)
        ufx, ufy = ux - ux0, uy - uy0

        u00 = self.u[self._u_idx(ux0, uy0)]
        u10 = self.u[self._u_idx(ux1, uy0)]
        u01 = self.u[self._u_idx(ux0, uy1)]
        u11 = self.u[self._u_idx(ux1, uy1)]
        u_val = (u00 * (1.0 - ufx) + u10 * ufx) * (1.0 - ufy) + (u01 * (1.0 - ufx) + u11 * ufx) * ufy

        # v is defined at (i + 0.5, j)
        vx = clamp_scalar(px - 0.5, 0.0, float(self.w - 1))
        vy = clamp_scalar(py, 0.0, float(self.h))
        vx0, vy0 = int(vx), int(vy)
        vx1 = min(vx0 + 1, self.w - 1)
        vy1 = min(vy0 + 1, self.h)
        vfx, vfy = vx - vx0, vy - vy0

        v00 = self.v[self._v_idx(vx0, vy0)]
        v10 = self.v[self._v_idx(vx1, vy0)]
        v01 = self.v[self._v_idx(vx0, vy1)]
        v11 = self.v[self._v_idx(vx1, vy1)]
        v_val = (v00 * (1.0 - vfx) + v10 * vfx) * (1.0 - vfy) + (v01 * (1.0 - vfx) + v11 * vfx) * vfy

        return u_val, v_val

    # -----------------------------------------------------------------------
    # Advection
    # -----------------------------------------------------------------------
    def advect_density(self, dt: float) -> None:
        """Advect density field using Semi-Lagrangian or MacCormack predictor-corrector."""
        new_density = [0.0] * (self.w * self.h)
        for y in range(self.h):
            for x in range(self.w):
                idx = self._c_idx(x, y)
                if self.solid[idx]:
                    new_density[idx] = 0.0
                    continue

                cx, cy = x + 0.5, y + 0.5
                u, v = self.sample_velocity_at(cx, cy)

                # Trace back in time (Semi-Lagrangian step)
                back_x = cx - u * dt / self.dx
                back_y = cy - v * dt / self.dx
                val_sl = self.sample_density_bilinear(back_x, back_y)

                if self.scheme == AdvectionScheme.MACCORMACK_BFECC:
                    # Forward trace from backward point
                    u_f, v_f = self.sample_velocity_at(back_x, back_y)
                    fwd_x = back_x + u_f * dt / self.dx
                    fwd_y = back_y + v_f * dt / self.dx
                    val_fwd = self.sample_density_bilinear(fwd_x, fwd_y)

                    # Error correction
                    corrected = val_sl + 0.5 * (self.density[idx] - val_fwd)

                    # Clamping with neighbors to avoid overshoots
                    x0 = max(0, min(self.w - 1, int(back_x - 0.5)))
                    y0 = max(0, min(self.h - 1, int(back_y - 0.5)))
                    x1 = min(self.w - 1, x0 + 1)
                    y1 = min(self.h - 1, y0 + 1)
                    min_val = min(self.density[self._c_idx(x0, y0)], self.density[self._c_idx(x1, y0)],
                                  self.density[self._c_idx(x0, y1)], self.density[self._c_idx(x1, y1)])
                    max_val = max(self.density[self._c_idx(x0, y0)], self.density[self._c_idx(x1, y0)],
                                  self.density[self._c_idx(x0, y1)], self.density[self._c_idx(x1, y1)])
                    new_density[idx] = max(0.0, clamp_scalar(corrected, min_val, max_val))
                else:
                    new_density[idx] = max(0.0, val_sl)

        self.density = new_density

    # -----------------------------------------------------------------------
    # Poisson Pressure Solver & Divergence Projection (∇ · u = 0)
    # -----------------------------------------------------------------------
    def project_pressure(self, iterations: int = 25) -> float:
        """
        Solves Poisson equation for pressure ∇²p = (ρ / Δt) ∇·u using Jacobi relaxation,
        then subtracts pressure gradient from face velocities to guarantee zero divergence.
        Returns maximum residual divergence.
        """
        # 1. Compute divergence at cell centers
        max_div = 0.0
        for y in range(self.h):
            for x in range(self.w):
                idx = self._c_idx(x, y)
                if self.solid[idx]:
                    self.divergence[idx] = 0.0
                    continue

                u_right = self.u[self._u_idx(x + 1, y)]
                u_left = self.u[self._u_idx(x, y)]
                v_top = self.v[self._v_idx(x, y + 1)]
                v_bottom = self.v[self._v_idx(x, y)]

                div = (u_right - u_left + v_top - v_bottom) / self.dx
                self.divergence[idx] = div
                max_div = max(max_div, abs(div))

        # 2. Jacobi relaxation for pressure Poisson equation: ∇²p = div
        new_pressure = [0.0] * (self.w * self.h)
        for _ in range(iterations):
            for y in range(self.h):
                for x in range(self.w):
                    idx = self._c_idx(x, y)
                    if self.solid[idx]:
                        new_pressure[idx] = 0.0
                        continue

                    p_left = self.pressure[self._c_idx(x - 1, y)] if x > 0 and not self.solid[self._c_idx(x - 1, y)] else self.pressure[idx]
                    p_right = self.pressure[self._c_idx(x + 1, y)] if x < self.w - 1 and not self.solid[self._c_idx(x + 1, y)] else self.pressure[idx]
                    p_bottom = self.pressure[self._c_idx(x, y - 1)] if y > 0 and not self.solid[self._c_idx(x, y - 1)] else self.pressure[idx]
                    p_top = self.pressure[self._c_idx(x, y + 1)] if y < self.h - 1 and not self.solid[self._c_idx(x, y + 1)] else self.pressure[idx]

                    # 4-point Laplacian stencil: (p_l + p_r + p_b + p_t - dx² * div) / 4
                    new_pressure[idx] = 0.25 * (p_left + p_right + p_bottom + p_top - self.dx * self.dx * self.divergence[idx])

            self.pressure, new_pressure = new_pressure, self.pressure

        # 3. Velocity projection: u -= ∇p
        for y in range(self.h):
            for x in range(1, self.w):
                if not self.solid[self._c_idx(x - 1, y)] and not self.solid[self._c_idx(x, y)]:
                    dp = (self.pressure[self._c_idx(x, y)] - self.pressure[self._c_idx(x - 1, y)]) / self.dx
                    self.u[self._u_idx(x, y)] -= dp

        for y in range(1, self.h):
            for x in range(self.w):
                if not self.solid[self._c_idx(x, y - 1)] and not self.solid[self._c_idx(x, y)]:
                    dp = (self.pressure[self._c_idx(x, y)] - self.pressure[self._c_idx(x, y - 1)]) / self.dx
                    self.v[self._v_idx(x, y)] -= dp

        # Enforce boundary conditions on domain borders (solid container)
        for y in range(self.h):
            self.u[self._u_idx(0, y)] = 0.0
            self.u[self._u_idx(self.w, y)] = 0.0
        for x in range(self.w):
            self.v[self._v_idx(x, 0)] = 0.0
            self.v[self._v_idx(x, self.h)] = 0.0

        return max_div

    # -----------------------------------------------------------------------
    # Simulation Step
    # -----------------------------------------------------------------------
    def step(self, dt: float, iterations: int = 20) -> float:
        """Performs a full fluid step: advection -> projection. Returns max divergence."""
        safe_dt = max(0.0001, dt)
        self.advect_density(safe_dt)
        max_div = self.project_pressure(iterations)
        return max_div

    def get_max_velocity(self) -> float:
        """Returns maximum scalar velocity magnitude in grid."""
        max_u = max(abs(x) for x in self.u) if self.u else 0.0
        max_v = max(abs(y) for y in self.v) if self.v else 0.0
        return math.sqrt(max_u * max_u + max_v * max_v)
