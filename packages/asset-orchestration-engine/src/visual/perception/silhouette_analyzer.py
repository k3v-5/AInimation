from typing import List, Tuple, Dict, Any
from ..capture.render_capture import CapturedView

class SilhouetteAnalyzer:
    @staticmethod
    def analyze_silhouette(view: CapturedView) -> Dict[str, Any]:
        grid = view.occupancy_grid
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        area = 0
        sum_x = 0
        sum_y = 0

        for y in range(height):
            for x in range(width):
                if grid[y][x] == 1:
                    area += 1
                    sum_x += x
                    sum_y += y

        centroid = (round(sum_x / area, 2), round(sum_y / area, 2)) if area > 0 else (0.0, 0.0)
        
        return {
            "area": area,
            "centroid": centroid,
            "bounding_box_2d": view.bounding_box_2d,
            "aspect_ratio": view.aspect_ratio,
            "resolution": view.resolution
        }
