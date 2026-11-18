import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class StrategyStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    EXPERIMENTAL = "EXPERIMENTAL"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

@dataclass
class StrategyRecord:
    strategy_id: str
    strategy_version: str = "1.0.0"
    strategy_signature: str = ""
    asset_type: str = "WEAPON"
    asset_class: str = "RIFLE"
    asset_complexity: str = "HIGH"
    input_features: Dict[str, Any] = field(default_factory=dict)
    reference_features: Dict[str, Any] = field(default_factory=dict)
    generation_method: str = "MODULAR_PARAMETRIC"
    geometry_method: str = "BEVEL_SUBD_SOLIDIFY"
    material_method: str = "PBR_METALLIC_ROUGHNESS"
    uv_method: str = "SMART_PROJECT_PACK"
    lod_method: str = "DECIMATE_3_LEVELS"
    collision_method: str = "UCX_CONVEX_HULLS"
    presentation_method: str = "TURNTABLE_STUDIO_LIGHT"
    estimated_cost: float = 100.0
    estimated_time: float = 30.0
    required_capabilities: List[str] = field(default_factory=lambda: ["CAP_GEOMETRY", "CAP_BLENDER"])
    required_tools: List[str] = field(default_factory=lambda: ["BlenderTool"])
    historical_success_rate: float = 1.0
    historical_failure_rate: float = 0.0
    historical_regression_rate: float = 0.0
    average_quality_score: float = 0.90
    average_recovery_count: float = 0.0
    average_correction_count: float = 0.0
    sample_count: int = 1
    confidence: float = 0.85
    status: StrategyStatus = StrategyStatus.ACTIVE
    parent_strategy_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "strategy_version": self.strategy_version,
            "strategy_signature": self.strategy_signature,
            "asset_type": self.asset_type,
            "asset_class": self.asset_class,
            "asset_complexity": self.asset_complexity,
            "input_features": self.input_features,
            "reference_features": self.reference_features,
            "generation_method": self.generation_method,
            "geometry_method": self.geometry_method,
            "material_method": self.material_method,
            "uv_method": self.uv_method,
            "lod_method": self.lod_method,
            "collision_method": self.collision_method,
            "presentation_method": self.presentation_method,
            "estimated_cost": round(self.estimated_cost, 4),
            "estimated_time": round(self.estimated_time, 4),
            "required_capabilities": self.required_capabilities,
            "required_tools": self.required_tools,
            "historical_success_rate": round(self.historical_success_rate, 4),
            "historical_failure_rate": round(self.historical_failure_rate, 4),
            "historical_regression_rate": round(self.historical_regression_rate, 4),
            "average_quality_score": round(self.average_quality_score, 4),
            "average_recovery_count": round(self.average_recovery_count, 4),
            "average_correction_count": round(self.average_correction_count, 4),
            "sample_count": self.sample_count,
            "confidence": round(self.confidence, 4),
            "status": self.status.value,
            "parent_strategy_id": self.parent_strategy_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategyRecord":
        return cls(
            strategy_id=data["strategy_id"],
            strategy_version=data.get("strategy_version", "1.0.0"),
            strategy_signature=data.get("strategy_signature", ""),
            asset_type=data.get("asset_type", "WEAPON"),
            asset_class=data.get("asset_class", "RIFLE"),
            asset_complexity=data.get("asset_complexity", "HIGH"),
            input_features=data.get("input_features", {}),
            reference_features=data.get("reference_features", {}),
            generation_method=data.get("generation_method", "MODULAR_PARAMETRIC"),
            geometry_method=data.get("geometry_method", "BEVEL_SUBD_SOLIDIFY"),
            material_method=data.get("material_method", "PBR_METALLIC_ROUGHNESS"),
            uv_method=data.get("uv_method", "SMART_PROJECT_PACK"),
            lod_method=data.get("lod_method", "DECIMATE_3_LEVELS"),
            collision_method=data.get("collision_method", "UCX_CONVEX_HULLS"),
            presentation_method=data.get("presentation_method", "TURNTABLE_STUDIO_LIGHT"),
            estimated_cost=data.get("estimated_cost", 100.0),
            estimated_time=data.get("estimated_time", 30.0),
            required_capabilities=data.get("required_capabilities", ["CAP_GEOMETRY", "CAP_BLENDER"]),
            required_tools=data.get("required_tools", ["BlenderTool"]),
            historical_success_rate=data.get("historical_success_rate", 1.0),
            historical_failure_rate=data.get("historical_failure_rate", 0.0),
            historical_regression_rate=data.get("historical_regression_rate", 0.0),
            average_quality_score=data.get("average_quality_score", 0.90),
            average_recovery_count=data.get("average_recovery_count", 0.0),
            average_correction_count=data.get("average_correction_count", 0.0),
            sample_count=data.get("sample_count", 1),
            confidence=data.get("confidence", 0.85),
            status=StrategyStatus(data.get("status", "ACTIVE")),
            parent_strategy_id=data.get("parent_strategy_id"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
