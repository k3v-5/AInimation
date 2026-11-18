from dataclasses import dataclass, field
from typing import Dict

@dataclass
class EvaluationProfile:
    name: str
    weights: Dict[str, float] = field(default_factory=dict)
    pass_threshold: float = 0.85
    max_repair_iterations: int = 3
    stagnation_threshold: float = 0.02

class ProfileRegistry:
    @staticmethod
    def get_profile(name: str = "BALANCED") -> EvaluationProfile:
        if name == "STRICT":
            return EvaluationProfile(
                name="STRICT",
                weights={
                    "SEMANTIC": 0.20, "SHAPE": 0.20, "PROPORTION": 0.15,
                    "SCALE": 0.15, "STYLE": 0.10, "MATERIAL": 0.10, "TECHNICAL": 0.10
                },
                pass_threshold=0.90,
                max_repair_iterations=3
            )
        elif name == "FAST":
            return EvaluationProfile(
                name="FAST",
                weights={
                    "SEMANTIC": 0.40, "SCALE": 0.30, "TECHNICAL": 0.30
                },
                pass_threshold=0.80,
                max_repair_iterations=2
            )
        else: # BALANCED
            return EvaluationProfile(
                name="BALANCED",
                weights={
                    "SEMANTIC": 0.25, "SHAPE": 0.20, "PROPORTION": 0.15,
                    "SCALE": 0.15, "STYLE": 0.10, "MATERIAL": 0.05, "TECHNICAL": 0.10
                },
                pass_threshold=0.85,
                max_repair_iterations=3
            )
