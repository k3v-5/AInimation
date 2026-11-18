"""
UAF-81.96: Spatial Telemetry Heatmap Generator.
Discretizes 2D/3D space into regular grid cells, accumulates event densities,
applies 2D Gaussian kernel smoothing and extracts high-intensity hotspots.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from ..core.contracts import (
    HeatmapMetric,
    HeatmapGrid2D,
    TelemetryEvent,
    TelemetryEventType,
    PlaytestRunResult,
    Vector3D,
)


class SpatialHeatmapGenerator:
    """
    Constructs normalized 2D density heatmaps from playtest telemetry runs.
    """

    def __init__(
        self,
        cell_size_m: float = 2.0,
        min_x: float = -50.0,
        max_x: float = 150.0,
        min_y: float = -50.0,
        max_y: float = 150.0,
    ):
        self.cell_size_m = max(0.5, cell_size_m)
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

        self.grid_width = max(1, int(math.ceil((max_x - min_x) / self.cell_size_m)))
        self.grid_height = max(1, int(math.ceil((max_y - min_y) / self.cell_size_m)))

    def _world_to_cell(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        if x < self.min_x or x > self.max_x or y < self.min_y or y > self.max_y:
            return None
        cx = int((x - self.min_x) / self.cell_size_m)
        cy = int((y - self.min_y) / self.cell_size_m)
        cx = min(self.grid_width - 1, max(0, cx))
        cy = min(self.grid_height - 1, max(0, cy))
        return cx, cy

    def _cell_to_world(self, cx: int, cy: int) -> Tuple[float, float]:
        wx = self.min_x + (cx + 0.5) * self.cell_size_m
        wy = self.min_y + (cy + 0.5) * self.cell_size_m
        return wx, wy

    def generate_heatmap(
        self,
        runs: List[PlaytestRunResult],
        metric: HeatmapMetric = HeatmapMetric.DEATH_DENSITY,
        apply_smoothing: bool = True,
        hotspot_threshold: float = 0.65,
    ) -> HeatmapGrid2D:
        """
        Processes telemetry events from playtest runs and produces a smoothed, normalized heatmap grid.
        """
        # Allocate zeroed grid: height x width
        raw_grid = [[0.0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        for run in runs:
            for evt in run.telemetry_events:
                weight = 0.0

                if metric == HeatmapMetric.DEATH_DENSITY and evt.event_type == TelemetryEventType.DEATH:
                    weight = 1.0
                elif metric == HeatmapMetric.AMMO_EXPENDITURE and evt.event_type == TelemetryEventType.FIRE_WEAPON:
                    weight = 1.0
                elif metric == HeatmapMetric.DAMAGE_TAKEN and evt.event_type == TelemetryEventType.TAKE_DAMAGE:
                    weight = float(evt.data.get("damage", 10.0))
                elif metric == HeatmapMetric.PATH_TRAVERSAL and evt.event_type in (
                    TelemetryEventType.ROOM_ENTER,
                    TelemetryEventType.SPAWN,
                    TelemetryEventType.GOAL_REACHED,
                ):
                    weight = 1.0
                elif metric == HeatmapMetric.DWELL_TIME and evt.event_type in (
                    TelemetryEventType.HIT_ENEMY,
                    TelemetryEventType.SOLVE_PUZZLE,
                    TelemetryEventType.TAKE_DAMAGE,
                ):
                    weight = 1.0

                if weight > 0.0:
                    coords = self._world_to_cell(evt.position.x, evt.position.y)
                    if coords:
                        cx, cy = coords
                        raw_grid[cy][cx] += weight

        # Apply smoothing if requested
        smoothed_grid = raw_grid
        if apply_smoothing:
            smoothed_grid = self._apply_gaussian_kernel(raw_grid)

        # Normalize grid to [0.0, 1.0]
        max_val = 0.0
        for row in smoothed_grid:
            for val in row:
                if val > max_val:
                    max_val = val

        normalized_cells = [
            [(round(val / max_val, 4) if max_val > 0 else 0.0) for val in row]
            for row in smoothed_grid
        ]

        # Extract hotspots
        hotspots: List[Dict[str, Any]] = []
        for cy in range(self.grid_height):
            for cx in range(self.grid_width):
                score = normalized_cells[cy][cx]
                if score >= hotspot_threshold:
                    wx, wy = self._cell_to_world(cx, cy)
                    hotspots.append(
                        {
                            "cell_x": cx,
                            "cell_y": cy,
                            "world_x": round(wx, 2),
                            "world_y": round(wy, 2),
                            "intensity": score,
                            "metric": metric.value,
                        }
                    )

        hotspots.sort(key=lambda h: h["intensity"], reverse=True)

        return HeatmapGrid2D(
            metric=metric,
            cell_size_m=self.cell_size_m,
            min_x=self.min_x,
            max_x=self.max_x,
            min_y=self.min_y,
            max_y=self.max_y,
            grid_width=self.grid_width,
            grid_height=self.grid_height,
            cells=normalized_cells,
            hotspots=hotspots,
        )

    def _apply_gaussian_kernel(self, grid: List[List[float]]) -> List[List[float]]:
        """
        Approximates a 3x3 Gaussian convolution:
        [[1, 2, 1],
         [2, 4, 2],
         [1, 2, 1]] / 16.0
        """
        kernel = [
            [1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0],
            [2.0 / 16.0, 4.0 / 16.0, 2.0 / 16.0],
            [1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0],
        ]

        out = [[0.0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                acc = 0.0
                for dy in range(-1, 2):
                    ny = y + dy
                    if 0 <= ny < self.grid_height:
                        for dx in range(-1, 2):
                            nx = x + dx
                            if 0 <= nx < self.grid_width:
                                k_val = kernel[dy + 1][dx + 1]
                                acc += grid[ny][nx] * k_val
                out[y][x] = acc

        return out
