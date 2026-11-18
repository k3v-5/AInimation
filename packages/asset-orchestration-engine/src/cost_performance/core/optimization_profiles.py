from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum

class ProfileType(str, Enum):
    QUALITY_FIRST = "QUALITY_FIRST"
    BALANCED = "BALANCED"
    PERFORMANCE_FIRST = "PERFORMANCE_FIRST"
    MEMORY_FIRST = "MEMORY_FIRST"
    FAST_ITERATION = "FAST_ITERATION"
    UNREAL_RUNTIME = "UNREAL_RUNTIME"

@dataclass
class OptimizationProfile:
    profile_type: ProfileType
    weight_quality: float = 0.40
    weight_cost: float = 0.15
    weight_performance: float = 0.20
    weight_memory: float = 0.10
    weight_time: float = 0.10
    weight_risk: float = 0.05

    def calculate_score(
        self,
        quality_val: float,
        cost_norm: float,
        perf_norm: float,
        memory_norm: float,
        time_norm: float,
        risk_val: float
    ) -> float:
        """
        OptimizationScore =
            QualityValue * W_q
            + PerformanceNorm * W_p
            + CostNorm * W_c
            + MemoryNorm * W_m
            + TimeNorm * W_t
            - RiskPenalty * W_r
        """
        score = (
            (quality_val * self.weight_quality) +
            (perf_norm * self.weight_performance) +
            (cost_norm * self.weight_cost) +
            (memory_norm * self.weight_memory) +
            (time_norm * self.weight_time) -
            (risk_val * self.weight_risk)
        )
        return round(max(0.0, min(1.0, score)), 4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_type": self.profile_type.value,
            "weight_quality": self.weight_quality,
            "weight_cost": self.weight_cost,
            "weight_performance": self.weight_performance,
            "weight_memory": self.weight_memory,
            "weight_time": self.weight_time,
            "weight_risk": self.weight_risk
        }

    @classmethod
    def quality_first(cls) -> "OptimizationProfile":
        return cls(ProfileType.QUALITY_FIRST, weight_quality=0.65, weight_cost=0.05, weight_performance=0.15, weight_memory=0.05, weight_time=0.05, weight_risk=0.05)

    @classmethod
    def balanced(cls) -> "OptimizationProfile":
        return cls(ProfileType.BALANCED, weight_quality=0.35, weight_cost=0.15, weight_performance=0.25, weight_memory=0.10, weight_time=0.10, weight_risk=0.05)

    @classmethod
    def performance_first(cls) -> "OptimizationProfile":
        return cls(ProfileType.PERFORMANCE_FIRST, weight_quality=0.20, weight_cost=0.15, weight_performance=0.40, weight_memory=0.15, weight_time=0.05, weight_risk=0.05)

    @classmethod
    def memory_first(cls) -> "OptimizationProfile":
        return cls(ProfileType.MEMORY_FIRST, weight_quality=0.25, weight_cost=0.10, weight_performance=0.20, weight_memory=0.35, weight_time=0.05, weight_risk=0.05)

    @classmethod
    def fast_iteration(cls) -> "OptimizationProfile":
        return cls(ProfileType.FAST_ITERATION, weight_quality=0.25, weight_cost=0.15, weight_performance=0.15, weight_memory=0.10, weight_time=0.30, weight_risk=0.05)

    @classmethod
    def unreal_runtime(cls) -> "OptimizationProfile":
        return cls(ProfileType.UNREAL_RUNTIME, weight_quality=0.30, weight_cost=0.10, weight_performance=0.35, weight_memory=0.15, weight_time=0.05, weight_risk=0.05)
