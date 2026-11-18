import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class MeasurementMethod(str, Enum):
    MEASURED = "MEASURED"
    ESTIMATED = "ESTIMATED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"

@dataclass
class CostMetric:
    name: str
    unit: str
    value: float
    source: str = "AOE_Profiler"
    timestamp: float = field(default_factory=time.time)
    confidence: float = 1.0
    measurement_method: MeasurementMethod = MeasurementMethod.MEASURED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "unit": self.unit,
            "value": round(self.value, 4),
            "source": self.source,
            "timestamp": self.timestamp,
            "confidence": round(self.confidence, 4),
            "measurement_method": self.measurement_method.value
        }

@dataclass
class CostReport:
    generation_time: float = 30.0
    evaluation_time: float = 5.0
    optimization_time: float = 2.0
    memory_usage_mb: float = 250.0
    disk_usage_mb: float = 15.0
    polygon_cost: float = 10.0
    material_cost: float = 5.0
    texture_cost: float = 20.0
    lod_cost: float = 5.0
    collision_cost: float = 2.0
    blender_execution_cost: float = 15.0
    export_cost: float = 5.0
    packaging_cost: float = 5.0
    estimated_unreal_runtime_cost: float = 12.0
    failure_risk: float = 0.05
    regeneration_cost: float = 10.0
    total_cost: float = 0.0
    metrics: Dict[str, CostMetric] = field(default_factory=dict)

    def __post_init__(self):
        if self.total_cost == 0.0:
            self.total_cost = (
                self.generation_time * 0.5 +
                self.memory_usage_mb * 0.2 +
                self.disk_usage_mb * 0.5 +
                self.estimated_unreal_runtime_cost * 1.5 +
                self.texture_cost +
                self.polygon_cost
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation_time": round(self.generation_time, 4),
            "evaluation_time": round(self.evaluation_time, 4),
            "optimization_time": round(self.optimization_time, 4),
            "memory_usage_mb": round(self.memory_usage_mb, 4),
            "disk_usage_mb": round(self.disk_usage_mb, 4),
            "polygon_cost": round(self.polygon_cost, 4),
            "material_cost": round(self.material_cost, 4),
            "texture_cost": round(self.texture_cost, 4),
            "lod_cost": round(self.lod_cost, 4),
            "collision_cost": round(self.collision_cost, 4),
            "blender_execution_cost": round(self.blender_execution_cost, 4),
            "export_cost": round(self.export_cost, 4),
            "packaging_cost": round(self.packaging_cost, 4),
            "estimated_unreal_runtime_cost": round(self.estimated_unreal_runtime_cost, 4),
            "failure_risk": round(self.failure_risk, 4),
            "regeneration_cost": round(self.regeneration_cost, 4),
            "total_cost": round(self.total_cost, 4),
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()}
        }
