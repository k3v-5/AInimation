import math
from typing import Dict, Any, Optional, Tuple
from ..core.scene_graph import SceneGraph, SceneNode

class ChangeAnalyzer:
    def __init__(self, abs_tolerance: float = 0.001, rel_tolerance: float = 0.01):
        self.abs_tolerance = abs_tolerance
        self.rel_tolerance = rel_tolerance

    def is_close(self, a: float, b: float) -> bool:
        return math.isclose(a, b, abs_tol=self.abs_tolerance, rel_tol=self.rel_tolerance)

    def is_vector_close(self, v1: tuple, v2: tuple) -> bool:
        if len(v1) != len(v2):
            return False
        return all(self.is_close(a, b) for a, b in zip(v1, v2))

    def analyze_node_modification(self, current_node: SceneNode, requested_changes: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Devuelve (es_no_op, cambios_reales_necesarios)
        Si todos los cambios pedidos ya están presentes en el nodo dentro de tolerancia -> (True, {})
        """
        real_changes = {}
        for prop, new_val in requested_changes.items():
            if not hasattr(current_node, prop):
                real_changes[prop] = new_val
                continue

            current_val = getattr(current_node, prop)

            if prop == "dimensions":
                # new_val puede ser DimensionsSpec o dict
                nh = getattr(new_val, "height", new_val.get("height", current_val.height) if isinstance(new_val, dict) else current_val.height)
                nw = getattr(new_val, "width", new_val.get("width", current_val.width) if isinstance(new_val, dict) else current_val.width)
                nd = getattr(new_val, "depth", new_val.get("depth", current_val.depth) if isinstance(new_val, dict) else current_val.depth)
                if not (self.is_close(current_val.height, nh) and self.is_close(current_val.width, nw) and self.is_close(current_val.depth, nd)):
                    real_changes[prop] = new_val
            elif prop == "local_transform":
                # comparar location, rotation, scale
                nl = getattr(new_val, "location", new_val.get("location", current_val.location) if isinstance(new_val, dict) else current_val.location)
                nr = getattr(new_val, "rotation", new_val.get("rotation", current_val.rotation) if isinstance(new_val, dict) else current_val.rotation)
                ns = getattr(new_val, "scale", new_val.get("scale", current_val.scale) if isinstance(new_val, dict) else current_val.scale)
                if not (self.is_vector_close(current_val.location, nl) and self.is_vector_close(current_val.rotation, nr) and self.is_vector_close(current_val.scale, ns)):
                    real_changes[prop] = new_val
            elif isinstance(current_val, (int, float)) and isinstance(new_val, (int, float)):
                if not self.is_close(current_val, new_val):
                    real_changes[prop] = new_val
            elif isinstance(current_val, (tuple, list)) and isinstance(new_val, (tuple, list)):
                if not self.is_vector_close(current_val, new_val):
                    real_changes[prop] = new_val
            else:
                if current_val != new_val:
                    real_changes[prop] = new_val

        is_no_op = len(real_changes) == 0
        return is_no_op, real_changes
