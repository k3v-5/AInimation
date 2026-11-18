from dataclasses import dataclass
from typing import Dict, Any
from .quality_gate import QualityWeights

@dataclass
class QualityProfile:
    name: str
    weights: QualityWeights
    pass_threshold: float = 0.90
    dimension_tolerance: float = 0.005
    silhouette_threshold: float = 0.85

class ThresholdManager:
    PROFILES = {
        "GENERIC": QualityProfile(name="GENERIC", weights=QualityWeights(0.35, 0.45, 0.20), pass_threshold=0.88),
        "GAME_ASSET": QualityProfile(name="GAME_ASSET", weights=QualityWeights(0.40, 0.40, 0.20), pass_threshold=0.90),
        "PROP": QualityProfile(name="PROP", weights=QualityWeights(0.30, 0.50, 0.20), pass_threshold=0.85),
    }

    @classmethod
    def get_profile(cls, name: str = "GAME_ASSET") -> QualityProfile:
        return cls.PROFILES.get(name.upper(), cls.PROFILES["GAME_ASSET"])
