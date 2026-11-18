from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
from .camera_manager import CameraConfig, ViewOrientation
from ...geometry.generators.base_generator import GeneratedGeometry

@dataclass
class CapturedView:
    orientation: ViewOrientation
    resolution: Tuple[int, int] # (width, height)
    occupancy_grid: List[List[int]] # Matriz binaria 0/1 de silueta proyectada
    bounding_box_2d: Tuple[int, int, int, int] # (min_x, min_y, max_x, max_y)
    component_bounds_2d: Dict[str, Tuple[int, int, int, int]] = field(default_factory=dict)
    aspect_ratio: float = 1.0

class RenderCapture:
    @staticmethod
    def capture_projected_view(
        components_geometry: Dict[str, GeneratedGeometry],
        camera: CameraConfig,
        grid_size: int = 64
    ) -> CapturedView:
        """
        Proyecta ortográficamente los vértices 3D en una cuadrícula binaria 2D normalizada.
        """
        grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        comp_2d_bounds: Dict[str, Tuple[int, int, int, int]] = {}

        # Determinar plano de proyección según la orientación
        # FRONT: X horizontal, Z vertical
        # SIDE: Y horizontal, Z vertical
        # TOP: X horizontal, Y vertical
        all_pts_2d: List[Tuple[float, float]] = []

        for cid, geo in components_geometry.items():
            c_pts_2d: List[Tuple[float, float]] = []
            for vx, vy, vz in geo.vertices:
                if camera.orientation in [ViewOrientation.FRONT, ViewOrientation.BACK]:
                    pt = (vx, vz)
                elif camera.orientation in [ViewOrientation.LEFT, ViewOrientation.RIGHT]:
                    pt = (vy, vz)
                else: # TOP, BOTTOM
                    pt = (vx, vy)
                c_pts_2d.append(pt)
                all_pts_2d.append(pt)

            if c_pts_2d:
                min_u = min(p[0] for p in c_pts_2d)
                max_u = max(p[0] for p in c_pts_2d)
                min_v = min(p[1] for p in c_pts_2d)
                max_v = max(p[1] for p in c_pts_2d)
                comp_2d_bounds[cid] = (int(min_u * 100), int(min_v * 100), int(max_u * 100), int(max_v * 100))

        if not all_pts_2d:
            return CapturedView(camera.orientation, (grid_size, grid_size), grid, (0, 0, 0, 0), {})

        # Normalizar a grid con margen (80% occupancy)
        min_u = min(p[0] for p in all_pts_2d)
        max_u = max(p[0] for p in all_pts_2d)
        min_v = min(p[1] for p in all_pts_2d)
        max_v = max(p[1] for p in all_pts_2d)

        range_u = max(max_u - min_u, 0.001)
        range_v = max(max_v - min_v, 0.001)
        max_range = max(range_u, range_v)

        margin = int(grid_size * 0.10)
        drawable_size = grid_size - 2 * margin

        for cid, geo in components_geometry.items():
            for vx, vy, vz in geo.vertices:
                if camera.orientation in [ViewOrientation.FRONT, ViewOrientation.BACK]:
                    u, v = vx, vz
                elif camera.orientation in [ViewOrientation.LEFT, ViewOrientation.RIGHT]:
                    u, v = vy, vz
                else:
                    u, v = vx, vy

                gu = margin + int(((u - min_u) / max_range) * (drawable_size - 1))
                gv = margin + int(((v - min_v) / max_range) * (drawable_size - 1))

                gu = max(0, min(grid_size - 1, gu))
                gv = max(0, min(grid_size - 1, gv))
                grid[gv][gu] = 1

        # Rellenar bounding box del objeto en el grid
        min_gx = grid_size
        max_gx = 0
        min_gy = grid_size
        max_gy = 0
        for y in range(grid_size):
            for x in range(grid_size):
                if grid[y][x] == 1:
                    min_gx = min(min_gx, x)
                    max_gx = max(max_gx, x)
                    min_gy = min(min_gy, y)
                    max_gy = max(max_gy, y)

        if min_gx > max_gx:
            min_gx, max_gx, min_gy, max_gy = 0, 0, 0, 0

        aspect = (max_u - min_u) / max(max_v - min_v, 0.001)

        return CapturedView(
            orientation=camera.orientation,
            resolution=(grid_size, grid_size),
            occupancy_grid=grid,
            bounding_box_2d=(min_gx, min_gy, max_gx, max_gy),
            component_bounds_2d=comp_2d_bounds,
            aspect_ratio=aspect
        )
