import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class FinalStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"
    REGRESSED = "REGRESSED"
    ABORTED = "ABORTED"

@dataclass
class StrategyOutcome:
    execution_id: str
    strategy_id: str
    semantic_id: str
    asset_id: Optional[str] = None
    success: bool = True
    quality_score: float = 0.90
    visual_score: float = 0.90
    geometry_score: float = 0.90
    material_score: float = 0.90
    uv_score: float = 0.90
    lod_score: float = 0.90
    collision_score: float = 0.90
    unreal_readiness_score: float = 0.95
    generation_time: float = 30.0
    resource_cost: float = 100.0
    token_cost: int = 1500
    tool_calls: int = 4
    blender_calls: int = 1
    failure_count: int = 0
    correction_count: int = 0
    recovery_count: int = 0
    regression_detected: bool = False
    golden_asset_delta: float = 0.0
    final_status: FinalStatus = FinalStatus.SUCCESS
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "strategy_id": self.strategy_id,
            "semantic_id": self.semantic_id,
            "asset_id": self.asset_id,
            "success": self.success,
            "quality_score": round(self.quality_score, 4),
            "visual_score": round(self.visual_score, 4),
            "geometry_score": round(self.geometry_score, 4),
            "material_score": round(self.material_score, 4),
            "uv_score": round(self.uv_score, 4),
            "lod_score": round(self.lod_score, 4),
            "collision_score": round(self.collision_score, 4),
            "unreal_readiness_score": round(self.unreal_readiness_score, 4),
            "generation_time": round(self.generation_time, 4),
            "resource_cost": round(self.resource_cost, 4),
            "token_cost": self.token_cost,
            "tool_calls": self.tool_calls,
            "blender_calls": self.blender_calls,
            "failure_count": self.failure_count,
            "correction_count": self.correction_count,
            "recovery_count": self.recovery_count,
            "regression_detected": self.regression_detected,
            "golden_asset_delta": round(self.golden_asset_delta, 4),
            "final_status": self.final_status.value,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategyOutcome":
        return cls(
            execution_id=data["execution_id"],
            strategy_id=data["strategy_id"],
            semantic_id=data["semantic_id"],
            asset_id=data.get("asset_id"),
            success=data.get("success", True),
            quality_score=data.get("quality_score", 0.90),
            visual_score=data.get("visual_score", 0.90),
            geometry_score=data.get("geometry_score", 0.90),
            material_score=data.get("material_score", 0.90),
            uv_score=data.get("uv_score", 0.90),
            lod_score=data.get("lod_score", 0.90),
            collision_score=data.get("collision_score", 0.90),
            unreal_readiness_score=data.get("unreal_readiness_score", 0.95),
            generation_time=data.get("generation_time", 30.0),
            resource_cost=data.get("resource_cost", 100.0),
            token_cost=data.get("token_cost", 1500),
            tool_calls=data.get("tool_calls", 4),
            blender_calls=data.get("blender_calls", 1),
            failure_count=data.get("failure_count", 0),
            correction_count=data.get("correction_count", 0),
            recovery_count=data.get("recovery_count", 0),
            regression_detected=data.get("regression_detected", False),
            golden_asset_delta=data.get("golden_asset_delta", 0.0),
            final_status=FinalStatus(data.get("final_status", "SUCCESS")),
            timestamp=data.get("timestamp", time.time())
        )

@dataclass
class LearningEvent:
    event_id: str
    strategy_id: str
    semantic_id: str
    event_type: str
    delta_quality: float = 0.0
    delta_confidence: float = 0.0
    reason: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "strategy_id": self.strategy_id,
            "semantic_id": self.semantic_id,
            "event_type": self.event_type,
            "delta_quality": round(self.delta_quality, 4),
            "delta_confidence": round(self.delta_confidence, 4),
            "reason": self.reason,
            "timestamp": self.timestamp
        }

@dataclass
class StrategyOptimizationProfile:
    profile_id: str
    name: str = "BALANCED"
    weight_quality: float = 0.40
    weight_visual: float = 0.15
    weight_engine_readiness: float = 0.15
    weight_reliability: float = 0.15
    weight_cost: float = 0.05
    weight_time: float = 0.05
    weight_confidence: float = 0.05
    max_allowed_regression: float = 0.00
    exploration_rate: float = 0.10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "weight_quality": self.weight_quality,
            "weight_visual": self.weight_visual,
            "weight_engine_readiness": self.weight_engine_readiness,
            "weight_reliability": self.weight_reliability,
            "weight_cost": self.weight_cost,
            "weight_time": self.weight_time,
            "weight_confidence": self.weight_confidence,
            "max_allowed_regression": self.max_allowed_regression,
            "exploration_rate": self.exploration_rate
        }

    @classmethod
    def quality_first(cls) -> "StrategyOptimizationProfile":
        return cls("PROFILE_QUALITY_FIRST", "QUALITY_FIRST", weight_quality=0.60, weight_visual=0.20, weight_engine_readiness=0.15, weight_cost=0.01, weight_time=0.01, weight_reliability=0.03)

    @classmethod
    def performance_first(cls) -> "StrategyOptimizationProfile":
        return cls("PROFILE_PERF_FIRST", "PERFORMANCE_FIRST", weight_quality=0.25, weight_cost=0.25, weight_time=0.25, weight_reliability=0.25)

    @classmethod
    def balanced(cls) -> "StrategyOptimizationProfile":
        return cls("PROFILE_BALANCED", "BALANCED")
