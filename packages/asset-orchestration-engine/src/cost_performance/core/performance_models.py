from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .cost_models import MeasurementMethod

@dataclass
class PerformanceReport:
    triangle_count: int = 15000
    vertex_count: int = 8000
    material_count: int = 2
    texture_count: int = 4
    texture_memory_mb: float = 16.0
    mesh_memory_mb: float = 2.5
    lod_count: int = 3
    lod_triangle_distribution: List[int] = field(default_factory=lambda: [15000, 7500, 3000])
    collision_complexity: str = "UCX_CONVEX"
    collision_hull_count: int = 6
    draw_call_estimate: int = 2
    nanite_compatibility: bool = True
    shader_complexity_estimate: str = "OPTIMIZED_PBR"
    overdraw_estimate: float = 1.05
    asset_memory_estimate_mb: float = 18.5
    runtime_risk: float = 0.05
    measurement_method: MeasurementMethod = MeasurementMethod.MEASURED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triangle_count": self.triangle_count,
            "vertex_count": self.vertex_count,
            "material_count": self.material_count,
            "texture_count": self.texture_count,
            "texture_memory_mb": round(self.texture_memory_mb, 4),
            "mesh_memory_mb": round(self.mesh_memory_mb, 4),
            "lod_count": self.lod_count,
            "lod_triangle_distribution": self.lod_triangle_distribution,
            "collision_complexity": self.collision_complexity,
            "collision_hull_count": self.collision_hull_count,
            "draw_call_estimate": self.draw_call_estimate,
            "nanite_compatibility": self.nanite_compatibility,
            "shader_complexity_estimate": self.shader_complexity_estimate,
            "overdraw_estimate": round(self.overdraw_estimate, 4),
            "asset_memory_estimate_mb": round(self.asset_memory_estimate_mb, 4),
            "runtime_risk": round(self.runtime_risk, 4),
            "measurement_method": self.measurement_method.value
        }
