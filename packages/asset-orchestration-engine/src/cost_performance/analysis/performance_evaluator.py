from typing import Dict, Any
from ..core.performance_models import PerformanceReport
from ..core.cost_models import MeasurementMethod

class PerformanceEvaluator:
    """Evaluates Unreal Engine runtime performance metrics."""

    @staticmethod
    def evaluate(raw_metrics: Dict[str, Any]) -> PerformanceReport:
        tris = raw_metrics.get("triangle_count", raw_metrics.get("polygon_count", 15000))
        verts = raw_metrics.get("vertex_count", int(tris * 0.55))
        mats = raw_metrics.get("material_count", 2)
        tex_mem = raw_metrics.get("texture_memory_mb", 16.0)
        mesh_mem = raw_metrics.get("mesh_memory_mb", round(tris * 0.00015, 2))

        return PerformanceReport(
            triangle_count=tris,
            vertex_count=verts,
            material_count=mats,
            texture_memory_mb=tex_mem,
            mesh_memory_mb=mesh_mem,
            asset_memory_estimate_mb=round(tex_mem + mesh_mem, 2),
            draw_call_estimate=mats,
            nanite_compatibility=tris >= 5000
        )
