"""
UAF-81.89.1: 3D Eulerian Navier-Stokes Fluid Grid.
Implements 3D Staggered MAC Grid, Thermal Buoyancy, 3D Vorticity Confinement, and Poisson Incompressibility.
"""

from __future__ import annotations

import math
from typing import List, Tuple
from ..core.contracts import (
    GridDimensions3D,
    FluidProperties,
    clamp_scalar,
    ensure_finite_scalar,
)


class EulerianFluidGrid3D:
    """
    3D Staggered MAC Grid for Volumetric Fluid Simulation (smoke, dust, atmospheric currents).
    """

    def __init__(self, dims: GridDimensions3D, props: FluidProperties = FluidProperties()) -> None:
        self.w: int = dims.width
        self.h: int = dims.height
        self.d: int = dims.depth
        self.dx: float = dims.cell_size
        self.props: FluidProperties = props

        # Staggered velocity components on cell faces
        self.u: List[float] = [0.0] * ((self.w + 1) * self.h * self.d)
        self.v: List[float] = [0.0] * (self.w * (self.h + 1) * self.d)
        self.w_vel: List[float] = [0.0] * (self.w * self.h * (self.d + 1))

        # Cell-centered scalars
        num_cells = self.w * self.h * self.d
        self.density: List[float] = [0.0] * num_cells
        self.temperature: List[float] = [self.props.ambient_temp] * num_cells
        self.pressure: List[float] = [0.0] * num_cells
        self.divergence: List[float] = [0.0] * num_cells
        self.solid: List[bool] = [False] * num_cells

    # -----------------------------------------------------------------------
    # Indexing Helpers
    # -----------------------------------------------------------------------
    def _c_idx(self, x: int, y: int, z: int) -> int:
        return (z * self.h + y) * self.w + x

    def _u_idx(self, x: int, y: int, z: int) -> int:
        return (z * self.h + y) * (self.w + 1) + x

    def _v_idx(self, x: int, y: int, z: int) -> int:
        return (z * (self.h + 1) + y) * self.w + x

    def _w_idx(self, x: int, y: int, z: int) -> int:
        return (z * self.h + y) * self.w + x

    # -----------------------------------------------------------------------
    # Injections
    # -----------------------------------------------------------------------
    def add_density(self, x: int, y: int, z: int, amount: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d:
            idx = self._c_idx(x, y, z)
            if not self.solid[idx]:
                self.density[idx] = max(0.0, self.density[idx] + amount)

    def add_temperature(self, x: int, y: int, z: int, delta_t: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d:
            idx = self._c_idx(x, y, z)
            if not self.solid[idx]:
                self.temperature[idx] += delta_t

    def add_velocity(self, x: int, y: int, z: int, vx: float, vy: float, vz: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d:
            self.u[self._u_idx(x, y, z)] += vx * 0.5
            self.u[self._u_idx(x + 1, y, z)] += vx * 0.5
            self.v[self._v_idx(x, y, z)] += vy * 0.5
            self.v[self._v_idx(x, y + 1, z)] += vy * 0.5
            self.w_vel[self._w_idx(x, y, z)] += vz * 0.5
            self.w_vel[self._w_idx(x, y, z + 1)] += vz * 0.5

    # -----------------------------------------------------------------------
    # Sampling
    # -----------------------------------------------------------------------
    def sample_density_trilinear(self, px: float, py: float, pz: float) -> float:
        """Sample density at continuous coordinate (px, py, pz)."""
        x = clamp_scalar(px - 0.5, 0.0, float(self.w - 1))
        y = clamp_scalar(py - 0.5, 0.0, float(self.h - 1))
        z = clamp_scalar(pz - 0.5, 0.0, float(self.d - 1))

        x0, y0, z0 = int(x), int(y), int(z)
        x1 = min(x0 + 1, self.w - 1)
        y1 = min(y0 + 1, self.h - 1)
        z1 = min(z0 + 1, self.d - 1)

        fx, fy, fz = x - x0, y - y0, z - z0

        c000 = self.density[self._c_idx(x0, y0, z0)]
        c100 = self.density[self._c_idx(x1, y0, z0)]
        c010 = self.density[self._c_idx(x0, y1, z0)]
        c110 = self.density[self._c_idx(x1, y1, z0)]
        c001 = self.density[self._c_idx(x0, y0, z1)]
        c101 = self.density[self._c_idx(x1, y0, z1)]
        c011 = self.density[self._c_idx(x0, y1, z1)]
        c111 = self.density[self._c_idx(x1, y1, z1)]

        c00 = c000 * (1 - fx) + c100 * fx
        c10 = c010 * (1 - fx) + c110 * fx
        c01 = c001 * (1 - fx) + c101 * fx
        c11 = c011 * (1 - fx) + c111 * fx

        c0 = c00 * (1 - fy) + c10 * fy
        c1 = c01 * (1 - fy) + c11 * fy

        return c0 * (1 - fz) + c1 * fz

    # -----------------------------------------------------------------------
    # Forces: Thermal Buoyancy & Vorticity Confinement
    # -----------------------------------------------------------------------
    def apply_buoyancy(self, dt: float) -> None:
        """Applies Boussinesq thermal buoyancy in vertical axis (Y)."""
        alpha = self.props.buoyancy_alpha
        beta = self.props.buoyancy_beta
        t_amb = self.props.ambient_temp

        for z in range(self.d):
            for y in range(1, self.h):
                for x in range(self.w):
                    c0 = self._c_idx(x, y - 1, z)
                    c1 = self._c_idx(x, y, z)
                    avg_density = 0.5 * (self.density[c0] + self.density[c1])
                    avg_temp = 0.5 * (self.temperature[c0] + self.temperature[c1])

                    # Buoyancy acceleration: f_y = -alpha * rho + beta * (T - T_amb)
                    f_y = -alpha * avg_density + beta * (avg_temp - t_amb)
                    self.v[self._v_idx(x, y, z)] += f_y * dt

    def apply_vorticity_confinement(self, dt: float) -> None:
        """
        Preserves microscopic eddies in smoke by calculating curl(u) and injecting
        restoring forces perpendicular to vorticity gradient.
        """
        eps = self.props.vorticity_epsilon
        if eps <= 0.0:
            return

        # Discrete curl at cell centers: omega = (dw/dy - dv/dz, du/dz - dw/dx, dv/dx - du/dy)
        curls: List[Tuple[float, float, float]] = []
        curl_mags: List[float] = []

        for z in range(self.d):
            for y in range(self.h):
                for x in range(self.w):
                    # Central differences for curl
                    dv_dx = (self.v[self._v_idx(min(x + 1, self.w - 1), y, z)] - self.v[self._v_idx(max(0, x - 1), y, z)]) / (2.0 * self.dx)
                    du_dy = (self.u[self._u_idx(x, min(y + 1, self.h - 1), z)] - self.u[self._u_idx(x, max(0, y - 1), z)]) / (2.0 * self.dx)

                    dw_dy = (self.w_vel[self._w_idx(x, min(y + 1, self.h - 1), z)] - self.w_vel[self._w_idx(x, max(0, y - 1), z)]) / (2.0 * self.dx)
                    dv_dz = (self.v[self._v_idx(x, y, min(z + 1, self.d - 1))] - self.v[self._v_idx(x, y, max(0, z - 1))]) / (2.0 * self.dx)

                    du_dz = (self.u[self._u_idx(x, y, min(z + 1, self.d - 1))] - self.u[self._u_idx(x, y, max(0, z - 1))]) / (2.0 * self.dx)
                    dw_dx = (self.w_vel[self._w_idx(min(x + 1, self.w - 1), y, z)] - self.w_vel[self._w_idx(max(0, x - 1), y, z)]) / (2.0 * self.dx)

                    om_x = dw_dy - dv_dz
                    om_y = du_dz - dw_dx
                    om_z = dv_dx - du_dy

                    mag = math.sqrt(om_x * om_x + om_y * om_y + om_z * om_z)
                    curls.append((om_x, om_y, om_z))
                    curl_mags.append(mag)

        # Apply confinement force f = eps * dx * (eta x omega)
        for z in range(1, self.d - 1):
            for y in range(1, self.h - 1):
                for x in range(1, self.w - 1):
                    idx = self._c_idx(x, y, z)
                    grad_x = (curl_mags[self._c_idx(x + 1, y, z)] - curl_mags[self._c_idx(x - 1, y, z)]) / (2.0 * self.dx)
                    grad_y = (curl_mags[self._c_idx(x, y + 1, z)] - curl_mags[self._c_idx(x, y - 1, z)]) / (2.0 * self.dx)
                    grad_z = (curl_mags[self._c_idx(x, y, z + 1)] - curl_mags[self._c_idx(x, y, z - 1)]) / (2.0 * self.dx)

                    g_len = math.sqrt(grad_x * grad_x + grad_y * grad_y + grad_z * grad_z) + 1e-6
                    eta_x, eta_y, eta_z = grad_x / g_len, grad_y / g_len, grad_z / g_len

                    om_x, om_y, om_z = curls[idx]
                    # Cross product: eta x omega
                    f_x = (eta_y * om_z - eta_z * om_y) * eps * self.dx
                    f_y = (eta_z * om_x - eta_x * om_z) * eps * self.dx
                    f_z = (eta_x * om_y - eta_y * om_x) * eps * self.dx

                    self.u[self._u_idx(x, y, z)] += f_x * dt
                    self.v[self._v_idx(x, y, z)] += f_y * dt
                    self.w_vel[self._w_idx(x, y, z)] += f_z * dt

    # -----------------------------------------------------------------------
    # 3D Incompressible Pressure Projection
    # -----------------------------------------------------------------------
    def project_pressure(self, iterations: int = 15) -> float:
        """
        Solves 3D Poisson equation for pressure: ∇²p = div and projects velocities to ∇·u = 0.
        """
        max_div = 0.0
        # 1. Compute 3D divergence: div = (du/dx + dv/dy + dw/dz)
        for z in range(self.d):
            for y in range(self.h):
                for x in range(self.w):
                    idx = self._c_idx(x, y, z)
                    du = self.u[self._u_idx(x + 1, y, z)] - self.u[self._u_idx(x, y, z)]
                    dv = self.v[self._v_idx(x, y + 1, z)] - self.v[self._v_idx(x, y, z)]
                    dw = self.w_vel[self._w_idx(x, y, z + 1)] - self.w_vel[self._w_idx(x, y, z)]
                    div = (du + dv + dw) / self.dx
                    self.divergence[idx] = div
                    max_div = max(max_div, abs(div))

        # 2. Jacobi relaxation for 3D Poisson: 6 neighbors
        new_pressure = [0.0] * (self.w * self.h * self.d)
        for _ in range(iterations):
            for z in range(self.d):
                for y in range(self.h):
                    for x in range(self.w):
                        idx = self._c_idx(x, y, z)
                        p_l = self.pressure[self._c_idx(x - 1, y, z)] if x > 0 else self.pressure[idx]
                        p_r = self.pressure[self._c_idx(x + 1, y, z)] if x < self.w - 1 else self.pressure[idx]
                        p_b = self.pressure[self._c_idx(x, y - 1, z)] if y > 0 else self.pressure[idx]
                        p_t = self.pressure[self._c_idx(x, y + 1, z)] if y < self.h - 1 else self.pressure[idx]
                        p_bk = self.pressure[self._c_idx(x, y, z - 1)] if z > 0 else self.pressure[idx]
                        p_fr = self.pressure[self._c_idx(x, y, z + 1)] if z < self.d - 1 else self.pressure[idx]

                        # 6-point 3D stencil
                        new_pressure[idx] = (p_l + p_r + p_b + p_t + p_bk + p_fr - self.dx * self.dx * self.divergence[idx]) / 6.0

            self.pressure, new_pressure = new_pressure, self.pressure

        # 3. Correct face velocities
        for z in range(self.d):
            for y in range(self.h):
                for x in range(1, self.w):
                    dp = (self.pressure[self._c_idx(x, y, z)] - self.pressure[self._c_idx(x - 1, y, z)]) / self.dx
                    self.u[self._u_idx(x, y, z)] -= dp

        for z in range(self.d):
            for y in range(1, self.h):
                for x in range(self.w):
                    dp = (self.pressure[self._c_idx(x, y, z)] - self.pressure[self._c_idx(x, y - 1, z)]) / self.dx
                    self.v[self._v_idx(x, y, z)] -= dp

        for z in range(1, self.d):
            for y in range(self.h):
                for x in range(self.w):
                    dp = (self.pressure[self._c_idx(x, y, z)] - self.pressure[self._c_idx(x, y, z - 1)]) / self.dx
                    self.w_vel[self._w_idx(x, y, z)] -= dp

        return max_div

    # -----------------------------------------------------------------------
    # Step
    # -----------------------------------------------------------------------
    def step(self, dt: float, iterations: int = 15) -> float:
        """Performs one full 3D fluid step. Returns max divergence."""
        safe_dt = max(0.0001, dt)
        self.apply_buoyancy(safe_dt)
        self.apply_vorticity_confinement(safe_dt)
        max_div = self.project_pressure(iterations)
        return max_div
