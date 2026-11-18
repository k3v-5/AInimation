"""
UAF-81.91: Thermal / Talus Relaxation and Scree Slope Erosion.
Models gravitational soil and rock collapse when slopes exceed the natural angle of repose.
"""

from __future__ import annotations

import math
from typing import Tuple

from uaf.landscape.core.contracts import Heightfield2D


class ThermalErosionSimulator:
    """
    Simulates thermal weathering and material slippage down steep cliffs.
    Relaxes cliffs above the angle of repose and deposits scree piles at cliff bases.
    """

    def __init__(
        self,
        angle_of_repose_deg: float = 34.0,
        relaxation_rate: float = 0.5,
    ):
        self.angle_of_repose_deg = angle_of_repose_deg
        self.tan_repose = math.tan(math.radians(angle_of_repose_deg))
        self.relaxation_rate = relaxation_rate

    def simulate(self, heightfield: Heightfield2D, iterations: int = 8) -> Heightfield2D:
        """
        Runs iterative thermal relaxation passes over the heightfield.
        Conserves total terrain volume strictly.
        """
        w, h = heightfield.width, heightfield.height
        vertical_scale = heightfield.max_elevation_meters - heightfield.min_elevation_meters
        cell_size = heightfield.meters_per_cell

        # Critical height difference threshold between adjacent orthogonal cells
        max_diff_ortho = (self.tan_repose * cell_size) / vertical_scale
        max_diff_diag = (self.tan_repose * cell_size * 1.41421356) / vertical_scale

        neighbors = [
            (-1, 0, max_diff_ortho),
            (1, 0, max_diff_ortho),
            (0, -1, max_diff_ortho),
            (0, 1, max_diff_ortho),
            (-1, -1, max_diff_diag),
            (1, -1, max_diff_diag),
            (-1, 1, max_diff_diag),
            (1, 1, max_diff_diag),
        ]

        for _ in range(iterations):
            # Accumulate material transfers to keep update order-independent
            delta_matrix = [[0.0 for _ in range(w)] for _ in range(h)]

            for y in range(h):
                for x in range(w):
                    curr_h = heightfield.get_elevation(x, y)

                    for ox, oy, max_diff in neighbors:
                        nx, ny = x + ox, y + oy
                        if 0 <= nx < w and 0 <= ny < h:
                            neighbor_h = heightfield.get_elevation(nx, ny)
                            diff = curr_h - neighbor_h

                            if diff > max_diff:
                                excess = (diff - max_diff) * self.relaxation_rate * 0.125
                                delta_matrix[y][x] -= excess
                                delta_matrix[ny][nx] += excess

            # Apply accumulated transfers
            for y in range(h):
                for x in range(w):
                    new_val = heightfield.get_elevation(x, y) + delta_matrix[y][x]
                    heightfield.set_elevation(x, y, new_val)

        return heightfield
