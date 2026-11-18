"""
UAF-81.89: High-performance Struct-of-Arrays (SoA) Particle Memory Buffer.
Optimized for SIMD auto-vectorization, cache-line coherence, and GPU compute staging.
"""

from __future__ import annotations

import struct
from typing import List, Tuple, Optional


class ParticleSoABuffer:
    """
    Struct-of-Arrays memory layout for high-density particle simulation.
    Keeps each attribute in contiguous memory arrays to minimize cache misses.
    """

    def __init__(self, capacity: int = 10000) -> None:
        self.capacity: int = max(1, capacity)
        self.count: int = 0

        # Contiguous attribute arrays
        self.pos_x: List[float] = [0.0] * self.capacity
        self.pos_y: List[float] = [0.0] * self.capacity
        self.pos_z: List[float] = [0.0] * self.capacity

        self.vel_x: List[float] = [0.0] * self.capacity
        self.vel_y: List[float] = [0.0] * self.capacity
        self.vel_z: List[float] = [0.0] * self.capacity

        self.life: List[float] = [0.0] * self.capacity
        self.max_life: List[float] = [1.0] * self.capacity
        self.size: List[float] = [1.0] * self.capacity

        self.col_r: List[float] = [1.0] * self.capacity
        self.col_g: List[float] = [1.0] * self.capacity
        self.col_b: List[float] = [1.0] * self.capacity
        self.col_a: List[float] = [1.0] * self.capacity

        self.alive: List[bool] = [False] * self.capacity

    def spawn(
        self,
        position: Tuple[float, float, float],
        velocity: Tuple[float, float, float],
        lifetime: float,
        size: float = 1.0,
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
    ) -> int:
        """Spawn a particle in the buffer. Returns particle slot index or -1 if full."""
        if self.count >= self.capacity:
            return -1

        idx = self.count
        self.pos_x[idx] = position[0]
        self.pos_y[idx] = position[1]
        self.pos_z[idx] = position[2]

        self.vel_x[idx] = velocity[0]
        self.vel_y[idx] = velocity[1]
        self.vel_z[idx] = velocity[2]

        self.life[idx] = lifetime
        self.max_life[idx] = max(0.0001, lifetime)
        self.size[idx] = size

        self.col_r[idx] = color[0]
        self.col_g[idx] = color[1]
        self.col_b[idx] = color[2]
        self.col_a[idx] = color[3]

        self.alive[idx] = True
        self.count += 1
        return idx

    def kill(self, idx: int) -> None:
        """Mark particle as dead and swap-with-back for O(1) removal and continuous compaction."""
        if 0 <= idx < self.count and self.alive[idx]:
            last_idx = self.count - 1
            if idx != last_idx:
                # Copy back particle into this slot
                self.pos_x[idx] = self.pos_x[last_idx]
                self.pos_y[idx] = self.pos_y[last_idx]
                self.pos_z[idx] = self.pos_z[last_idx]

                self.vel_x[idx] = self.vel_x[last_idx]
                self.vel_y[idx] = self.vel_y[last_idx]
                self.vel_z[idx] = self.vel_z[last_idx]

                self.life[idx] = self.life[last_idx]
                self.max_life[idx] = self.max_life[last_idx]
                self.size[idx] = self.size[last_idx]

                self.col_r[idx] = self.col_r[last_idx]
                self.col_g[idx] = self.col_g[last_idx]
                self.col_b[idx] = self.col_b[last_idx]
                self.col_a[idx] = self.col_a[last_idx]

                self.alive[idx] = self.alive[last_idx]

            self.alive[last_idx] = False
            self.count -= 1

    def update_lifecycle_and_motion(self, dt: float, gravity: Tuple[float, float, float] = (0.0, -9.81, 0.0)) -> int:
        """
        Integrate particle motion and update lifetimes using SoA sequential loops.
        Returns the number of particles that survived the frame.
        """
        gx, gy, gz = gravity
        i = 0
        while i < self.count:
            self.life[i] -= dt
            if self.life[i] <= 0.0:
                self.kill(i)
                continue  # Slot `i` now has the swapped particle from end, re-check index `i`

            # Velocity integration
            self.vel_x[i] += gx * dt
            self.vel_y[i] += gy * dt
            self.vel_z[i] += gz * dt

            # Position integration
            self.pos_x[i] += self.vel_x[i] * dt
            self.pos_y[i] += self.vel_y[i] * dt
            self.pos_z[i] += self.vel_z[i] * dt

            # Alpha fade by remaining life ratio
            life_ratio = max(0.0, min(1.0, self.life[i] / self.max_life[i]))
            self.col_a[i] = life_ratio

            i += 1

        return self.count

    def to_packed_bytes(self) -> bytes:
        """
        Packs active particles into a contiguous binary buffer suitable for GPU upload.
        Format per particle: float4(pos.xyz, size), float4(vel.xyz, life_ratio), float4(color.rgba) = 48 bytes.
        """
        buffer = bytearray(self.count * 48)
        offset = 0
        for i in range(self.count):
            life_ratio = self.life[i] / self.max_life[i] if self.max_life[i] > 0 else 0.0
            struct.pack_into(
                "<12f",
                buffer,
                offset,
                self.pos_x[i],
                self.pos_y[i],
                self.pos_z[i],
                self.size[i],
                self.vel_x[i],
                self.vel_y[i],
                self.vel_z[i],
                life_ratio,
                self.col_r[i],
                self.col_g[i],
                self.col_b[i],
                self.col_a[i],
            )
            offset += 48
        return bytes(buffer)
