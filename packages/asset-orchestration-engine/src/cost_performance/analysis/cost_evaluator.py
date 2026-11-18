from typing import Dict, Any
from ..core.cost_models import CostReport, CostMetric, MeasurementMethod

class CostEvaluator:
    """Evaluates raw operational and resource costs for asset candidates."""

    @staticmethod
    def evaluate(raw_metrics: Dict[str, Any]) -> CostReport:
        gen_time = raw_metrics.get("generation_time", 30.0)
        mem_mb = raw_metrics.get("memory_usage_mb", raw_metrics.get("memory_mb", 250.0))
        disk_mb = raw_metrics.get("disk_usage_mb", 15.0)
        tex_cost = raw_metrics.get("texture_cost", 20.0)
        poly_cost = raw_metrics.get("polygon_cost", 10.0)

        report = CostReport(
            generation_time=gen_time,
            memory_usage_mb=mem_mb,
            disk_usage_mb=disk_mb,
            texture_cost=tex_cost,
            polygon_cost=poly_cost
        )
        return report
