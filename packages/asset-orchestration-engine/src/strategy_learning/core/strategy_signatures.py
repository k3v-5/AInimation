import hashlib
import json
from typing import Dict, Any
from .feature_models import ProblemFeatures

class ProblemSignature:
    """Computes deterministic hash signature for comparable problem definitions."""

    @staticmethod
    def compute(features: ProblemFeatures) -> str:
        canonical = {
            "asset_category": features.asset_category,
            "asset_complexity": features.asset_complexity,
            "geometry_complexity": features.geometry_complexity,
            "material_complexity": features.material_complexity,
            "target_engine": features.target_engine,
            "lod_requirement": features.lod_requirement,
            "collision_requirement": features.collision_requirement
        }
        raw = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class StrategySignature:
    """Computes deterministic hash signature for generation strategies."""

    @staticmethod
    def compute(strategy_dict: Dict[str, Any]) -> str:
        canonical = {
            "asset_type": strategy_dict.get("asset_type", "WEAPON"),
            "generation_method": strategy_dict.get("generation_method", ""),
            "geometry_method": strategy_dict.get("geometry_method", ""),
            "material_method": strategy_dict.get("material_method", ""),
            "uv_method": strategy_dict.get("uv_method", ""),
            "lod_method": strategy_dict.get("lod_method", ""),
            "collision_method": strategy_dict.get("collision_method", "")
        }
        raw = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
