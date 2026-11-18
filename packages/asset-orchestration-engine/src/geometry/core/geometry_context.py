import time
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class GeometryMetrics:
    build_time_ms: float = 0.0
    validation_time_ms: float = 0.0
    vertex_count: int = 0
    triangle_count: int = 0
    objects_count: int = 0

class GeometryContext:
    def __init__(self):
        self.metrics = GeometryMetrics()
        self.logs: List[Dict[str, Any]] = []

    def record_metrics(self, build_time: float, vertices: int, triangles: int, objects: int = 1):
        self.metrics.build_time_ms = round(build_time * 1000, 2)
        self.metrics.vertex_count = vertices
        self.metrics.triangle_count = triangles
        self.metrics.objects_count = objects
