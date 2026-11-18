from typing import List, Tuple, Optional

class SilhouetteComparator:
    @staticmethod
    def calculate_iou(grid_a: List[List[int]], grid_b: List[List[int]]) -> float:
        """
        Calcula el Intersection over Union (IoU) entre dos matrices binarias 2D.
        """
        if not grid_a or not grid_b:
            return 0.0

        h = min(len(grid_a), len(grid_b))
        w = min(len(grid_a[0]), len(grid_b[0]))

        intersection = 0
        union = 0

        for y in range(h):
            for x in range(w):
                v_a = grid_a[y][x]
                v_b = grid_b[y][x]
                if v_a == 1 and v_b == 1:
                    intersection += 1
                if v_a == 1 or v_b == 1:
                    union += 1

        if union == 0:
            return 1.0 # Ambas vacías = idénticas
        return round(intersection / union, 4)

    @staticmethod
    def compare_aspect_ratios(aspect_a: float, aspect_b: float) -> float:
        """Score de similitud de aspecto [0.0, 1.0]."""
        if aspect_a <= 0 or aspect_b <= 0: return 0.0
        ratio = min(aspect_a, aspect_b) / max(aspect_a, aspect_b)
        return round(ratio, 4)
