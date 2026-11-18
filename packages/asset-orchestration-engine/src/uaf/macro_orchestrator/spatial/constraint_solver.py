"""
UAF-81.102: Spatial Constraint Solver.
Solves placement of interior modular WFC facilities onto macro-terrain heightfields,
carves level foundation pads with smooth blend falloffs, and aligns road network splines.
"""

from __future__ import annotations

import math
from typing import Tuple

from uaf.landscape.core.contracts import Heightfield2D
from uaf.macro_orchestrator.core.contracts import SpatialFootprint


class SpatialConstraintSolver:
    """
    Solves continuous geometric constraints for placing architectural installations
    directly onto procedural landscapes without clipping or float detachment.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def set_elevation_meters(heightfield: Heightfield2D, x: int, y: int, elevation_m: float) -> None:
        """Helper to set world elevation in meters on Heightfield2D by converting to normalized [0, 1]."""
        denom = heightfield.max_elevation_meters - heightfield.min_elevation_meters
        if denom > 1e-5:
            norm = (elevation_m - heightfield.min_elevation_meters) / denom
            heightfield.set_elevation(x, y, norm)

    def find_optimal_facility_plateau(
        self,
        heightfield: Heightfield2D,
        footprint_cells: Tuple[int, int] = (16, 16),
        margin_cells: int = 4,
    ) -> Tuple[int, int, float]:
        """
        Scans heightfield to find the flattest rectangular plateau (minimum elevation variance).
        Returns (best_origin_x, best_origin_y, average_elevation_meters).
        """
        fx, fy = footprint_cells
        w, h = heightfield.width, heightfield.height

        max_x = w - fx - margin_cells
        max_y = h - fy - margin_cells
        step = max(1, min(w, h) // 16)  # Adaptive search step

        best_x = margin_cells
        best_y = margin_cells
        min_variance = float("inf")
        best_avg_elev = 50.0

        for y in range(margin_cells, max_y + 1, step):
            for x in range(margin_cells, max_x + 1, step):
                elevations = []
                for cy in range(y, y + fy, max(1, fy // 4)):
                    for cx in range(x, x + fx, max(1, fx // 4)):
                        elevations.append(heightfield.get_world_elevation_meters(cx, cy))

                if not elevations:
                    continue

                avg_e = sum(elevations) / len(elevations)
                var = sum((e - avg_e) ** 2 for e in elevations) / len(elevations)

                if var < min_variance:
                    min_variance = var
                    best_x = x
                    best_y = y
                    best_avg_elev = avg_e

        return (best_x, best_y, round(best_avg_elev, 2))

    def carve_foundation_pad(
        self,
        heightfield: Heightfield2D,
        origin_x: int,
        origin_y: int,
        size_x: int,
        size_y: int,
        target_elevation_m: float,
        blend_radius_cells: int = 3,
    ) -> None:
        """
        Flattens the heightfield under the facility footprint to target_elevation_m
        and applies a smooth cosine falloff across blend_radius_cells to avoid sharp seams.
        """
        w, h = heightfield.width, heightfield.height

        min_scan_x = max(0, origin_x - blend_radius_cells)
        max_scan_x = min(w - 1, origin_x + size_x + blend_radius_cells)
        min_scan_y = max(0, origin_y - blend_radius_cells)
        max_scan_y = min(h - 1, origin_y + size_y + blend_radius_cells)

        for y in range(min_scan_y, max_scan_y + 1):
            for x in range(min_scan_x, max_scan_x + 1):
                inside_x = origin_x <= x < (origin_x + size_x)
                inside_y = origin_y <= y < (origin_y + size_y)

                if inside_x and inside_y:
                    self.set_elevation_meters(heightfield, x, y, target_elevation_m)
                else:
                    dx = max(0, origin_x - x, x - (origin_x + size_x - 1))
                    dy = max(0, origin_y - y, y - (origin_y + size_y - 1))
                    dist = math.hypot(dx, dy)

                    if dist <= blend_radius_cells:
                        alpha = 0.5 * (1.0 + math.cos(math.pi * (dist / blend_radius_cells)))
                        current_elev = heightfield.get_world_elevation_meters(x, y)
                        blended = current_elev * (1.0 - alpha) + target_elevation_m * alpha
                        self.set_elevation_meters(heightfield, x, y, blended)

    def solve_placement(
        self,
        heightfield: Heightfield2D,
        wfc_dimensions: Tuple[int, int],
        tile_size_meters: float = 6.0,
    ) -> SpatialFootprint:
        """
        Solves complete spatial placement of WFC facility onto the heightfield.
        """
        gw, gh = wfc_dimensions
        mpc = heightfield.meters_per_cell

        facility_width_m = gw * tile_size_meters
        facility_height_m = gh * tile_size_meters
        cells_x = max(4, int(math.ceil(facility_width_m / mpc)) + 2)
        cells_y = max(4, int(math.ceil(facility_height_m / mpc)) + 2)

        # 1. Find optimal plateau
        orig_x, orig_y, pad_elev_m = self.find_optimal_facility_plateau(
            heightfield, footprint_cells=(cells_x, cells_y)
        )

        # 2. Carve foundation pad
        self.carve_foundation_pad(
            heightfield,
            origin_x=orig_x,
            origin_y=orig_y,
            size_x=cells_x,
            size_y=cells_y,
            target_elevation_m=pad_elev_m,
            blend_radius_cells=3,
        )

        # 3. Calculate center world coordinate in Unreal cm (Z-up)
        center_cell_x = orig_x + cells_x / 2.0
        center_cell_y = orig_y + cells_y / 2.0
        center_x_cm = center_cell_x * mpc * 100.0
        center_y_cm = center_cell_y * mpc * 100.0
        center_z_cm = pad_elev_m * 100.0

        # Airlock entrance at bottom edge of facility footprint
        airlock_cell_x = orig_x + cells_x // 2
        airlock_cell_y = orig_y
        airlock_x_cm = airlock_cell_x * mpc * 100.0
        airlock_y_cm = airlock_cell_y * mpc * 100.0
        airlock_z_cm = center_z_cm

        terminus_coord = (airlock_cell_x, max(0, airlock_cell_y - 2))

        return SpatialFootprint(
            facility_id="facility_bunker_primary",
            center_world_cm=(round(center_x_cm, 2), round(center_y_cm, 2), round(center_z_cm, 2)),
            grid_origin_coord=(orig_x, orig_y),
            footprint_cells_x=cells_x,
            footprint_cells_y=cells_y,
            pad_elevation_m=pad_elev_m,
            entrance_airlock_cm=(round(airlock_x_cm, 2), round(airlock_y_cm, 2), round(airlock_z_cm, 2)),
            road_terminus_coord=terminus_coord,
            safety_buffer_cm=30.0,
        )
