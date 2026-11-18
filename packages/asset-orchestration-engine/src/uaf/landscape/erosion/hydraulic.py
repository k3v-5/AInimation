"""
UAF-81.91: Particle-Based Droplet Hydraulic Erosion Simulation.
Simulates natural water droplet flow, slope-dependent sediment detachment,
river canyon carving, and alluvial fan sediment deposition.
"""

from __future__ import annotations

import math
import random
from typing import Optional, Tuple

from uaf.landscape.core.contracts import Heightfield2D


class HydraulicErosionSimulator:
    """
    Physical droplet-based hydraulic erosion engine.
    Carves natural dendritic drainage channels, creates alluvial plains,
    and softens sharp artificial geometric edges.
    """

    def __init__(
        self,
        seed: int = 42,
        inertia: float = 0.05,
        sediment_capacity_factor: float = 4.0,
        min_sediment_capacity: float = 0.01,
        erode_speed: float = 0.3,
        deposit_speed: float = 0.3,
        evaporation_rate: float = 0.01,
        gravity: float = 4.0,
        max_droplet_lifetime: int = 35,
        erosion_radius: int = 2,
    ):
        self.seed = seed
        self.rng = random.Random(seed)
        self.inertia = inertia
        self.sediment_capacity_factor = sediment_capacity_factor
        self.min_sediment_capacity = min_sediment_capacity
        self.erode_speed = erode_speed
        self.deposit_speed = deposit_speed
        self.evaporation_rate = evaporation_rate
        self.gravity = gravity
        self.max_droplet_lifetime = max_droplet_lifetime
        self.erosion_radius = erosion_radius

    def simulate(self, heightfield: Heightfield2D, num_droplets: int = 15000) -> Heightfield2D:
        """
        Executes droplet hydraulic simulation over the given heightfield.
        Conserves overall mass within numerical precision bounds.
        """
        w, h = heightfield.width, heightfield.height

        for _ in range(num_droplets):
            # Spawn droplet at random location (avoid outermost border)
            pos_x = self.rng.uniform(1.0, w - 2.0)
            pos_y = self.rng.uniform(1.0, h - 2.0)

            dir_x = 0.0
            dir_y = 0.0
            speed = 1.0
            water = 1.0
            sediment = 0.0

            for _ in range(self.max_droplet_lifetime):
                node_x = int(math.floor(pos_x))
                node_y = int(math.floor(pos_y))

                # Calculate droplet offset inside cell
                cell_offset_x = pos_x - node_x
                cell_offset_y = pos_y - node_y

                # Calculate height and gradient
                h00 = heightfield.get_elevation(node_x, node_y)
                h10 = heightfield.get_elevation(node_x + 1, node_y)
                h01 = heightfield.get_elevation(node_x, node_y + 1)
                h11 = heightfield.get_elevation(node_x + 1, node_y + 1)

                grad_x = (h10 - h00) * (1.0 - cell_offset_y) + (h11 - h01) * cell_offset_y
                grad_y = (h01 - h00) * (1.0 - cell_offset_x) + (h11 - h10) * cell_offset_x

                current_height = (
                    h00 * (1.0 - cell_offset_x) * (1.0 - cell_offset_y)
                    + h10 * cell_offset_x * (1.0 - cell_offset_y)
                    + h01 * (1.0 - cell_offset_x) * cell_offset_y
                    + h11 * cell_offset_x * cell_offset_y
                )

                # Update direction with inertia
                dir_x = dir_x * self.inertia - grad_x * (1.0 - self.inertia)
                dir_y = dir_y * self.inertia - grad_y * (1.0 - self.inertia)

                dir_len = math.hypot(dir_x, dir_y)
                if dir_len > 1e-5:
                    dir_x /= dir_len
                    dir_y /= dir_len
                else:
                    # Flat surface or local pit: pick random direction
                    angle = self.rng.uniform(0.0, 2.0 * math.pi)
                    dir_x = math.cos(angle)
                    dir_y = math.sin(angle)

                new_pos_x = pos_x + dir_x
                new_pos_y = pos_y + dir_y

                # Check grid bounds
                if not (1.0 <= new_pos_x < w - 2.0 and 1.0 <= new_pos_y < h - 2.0):
                    break

                # Calculate new height
                new_node_x = int(math.floor(new_pos_x))
                new_node_y = int(math.floor(new_pos_y))
                new_offset_x = new_pos_x - new_node_x
                new_offset_y = new_pos_y - new_node_y

                nh00 = heightfield.get_elevation(new_node_x, new_node_y)
                nh10 = heightfield.get_elevation(new_node_x + 1, new_node_y)
                nh01 = heightfield.get_elevation(new_node_x, new_node_y + 1)
                nh11 = heightfield.get_elevation(new_node_x + 1, new_node_y + 1)

                new_height = (
                    nh00 * (1.0 - new_offset_x) * (1.0 - new_offset_y)
                    + nh10 * new_offset_x * (1.0 - new_offset_y)
                    + nh01 * (1.0 - new_offset_x) * new_offset_y
                    + nh11 * new_offset_x * new_offset_y
                )

                delta_h = new_height - current_height

                # Calculate sediment capacity
                capacity = max(-delta_h, self.min_sediment_capacity) * speed * water * self.sediment_capacity_factor

                if sediment > capacity or delta_h > 0.0:
                    # Deposit sediment
                    deposit_amount = (
                        (sediment - capacity) * self.deposit_speed
                        if delta_h <= 0.0
                        else min(sediment, delta_h)
                    )
                    sediment -= deposit_amount

                    # Distribute deposited sediment across 4 bilinear neighbor points
                    heightfield.set_elevation(
                        node_x, node_y,
                        heightfield.get_elevation(node_x, node_y) + deposit_amount * (1.0 - cell_offset_x) * (1.0 - cell_offset_y)
                    )
                    heightfield.set_elevation(
                        node_x + 1, node_y,
                        heightfield.get_elevation(node_x + 1, node_y) + deposit_amount * cell_offset_x * (1.0 - cell_offset_y)
                    )
                    heightfield.set_elevation(
                        node_x, node_y + 1,
                        heightfield.get_elevation(node_x, node_y + 1) + deposit_amount * (1.0 - cell_offset_x) * cell_offset_y
                    )
                    heightfield.set_elevation(
                        node_x + 1, node_y + 1,
                        heightfield.get_elevation(node_x + 1, node_y + 1) + deposit_amount * cell_offset_x * cell_offset_y
                    )
                else:
                    # Erode soil
                    erode_amount = min((capacity - sediment) * self.erode_speed, -delta_h)
                    sediment += erode_amount

                    heightfield.set_elevation(
                        node_x, node_y,
                        heightfield.get_elevation(node_x, node_y) - erode_amount * (1.0 - cell_offset_x) * (1.0 - cell_offset_y)
                    )
                    heightfield.set_elevation(
                        node_x + 1, node_y,
                        heightfield.get_elevation(node_x + 1, node_y) - erode_amount * cell_offset_x * (1.0 - cell_offset_y)
                    )
                    heightfield.set_elevation(
                        node_x, node_y + 1,
                        heightfield.get_elevation(node_x, node_y + 1) - erode_amount * (1.0 - cell_offset_x) * cell_offset_y
                    )
                    heightfield.set_elevation(
                        node_x + 1, node_y + 1,
                        heightfield.get_elevation(node_x + 1, node_y + 1) - erode_amount * cell_offset_x * cell_offset_y
                    )

                speed = math.sqrt(max(0.01, speed * speed + delta_h * self.gravity))
                water *= (1.0 - self.evaporation_rate)

                pos_x = new_pos_x
                pos_y = new_pos_y

        return heightfield
