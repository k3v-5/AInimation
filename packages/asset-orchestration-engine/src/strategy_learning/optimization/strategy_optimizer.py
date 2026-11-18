import time
from typing import Dict, Any, Optional
from ..core.strategy_models import StrategyRecord

class StrategyOptimizer:
    """Derives new optimized versions of strategies based on learning feedback."""

    @staticmethod
    def derive_optimized_version(
        base_strategy: StrategyRecord,
        param_deltas: Dict[str, Any],
        change_reason: str = "Performance optimization"
    ) -> StrategyRecord:
        new_version_num = str(int(base_strategy.strategy_version.split(".")[0]) + 1) + ".0.0"
        new_id = f"{base_strategy.strategy_id}_v{new_version_num}"

        new_features = dict(base_strategy.input_features)
        new_features.update(param_deltas)

        return StrategyRecord(
            strategy_id=new_id,
            strategy_version=new_version_num,
            parent_strategy_id=base_strategy.strategy_id,
            asset_type=base_strategy.asset_type,
            asset_class=base_strategy.asset_class,
            asset_complexity=base_strategy.asset_complexity,
            input_features=new_features,
            generation_method=base_strategy.generation_method,
            geometry_method=base_strategy.geometry_method,
            material_method=base_strategy.material_method,
            uv_method=base_strategy.uv_method,
            lod_method=base_strategy.lod_method,
            collision_method=base_strategy.collision_method,
            estimated_cost=base_strategy.estimated_cost * 0.9,
            estimated_time=base_strategy.estimated_time * 0.9,
            average_quality_score=base_strategy.average_quality_score,
            confidence=0.70, # Lower initial confidence for new version
            sample_count=0
        )
