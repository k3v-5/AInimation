from typing import Optional
from ..core.strategy_models import StrategyRecord

class TransferLearning:
    """Enables bounded knowledge transfer between related asset classes with confidence discount."""

    CLASS_SIMILARITIES = {
        ("RIFLE", "SMG"): 0.85,
        ("RIFLE", "SNIPER"): 0.80,
        ("RIFLE", "PISTOL"): 0.70,
        ("SMG", "PISTOL"): 0.85,
        ("PROP", "STRUCTURE"): 0.75
    }

    @classmethod
    def calculate_similarity(cls, class_a: str, class_b: str) -> float:
        if class_a == class_b:
            return 1.0
        pair = (class_a.upper(), class_b.upper())
        rev_pair = (class_b.upper(), class_a.upper())
        return cls.CLASS_SIMILARITIES.get(pair, cls.CLASS_SIMILARITIES.get(rev_pair, 0.40))

    @classmethod
    def transfer_strategy(
        cls,
        source_strategy: StrategyRecord,
        target_asset_class: str,
        new_strategy_id: str
    ) -> StrategyRecord:
        sim = cls.calculate_similarity(source_strategy.asset_class, target_asset_class)
        discounted_confidence = round(source_strategy.confidence * sim * 0.80, 4)

        return StrategyRecord(
            strategy_id=new_strategy_id,
            strategy_version="1.0.0-transfer",
            asset_type=source_strategy.asset_type,
            asset_class=target_asset_class,
            asset_complexity=source_strategy.asset_complexity,
            input_features=dict(source_strategy.input_features),
            generation_method=source_strategy.generation_method,
            geometry_method=source_strategy.geometry_method,
            material_method=source_strategy.material_method,
            uv_method=source_strategy.uv_method,
            lod_method=source_strategy.lod_method,
            collision_method=source_strategy.collision_method,
            average_quality_score=source_strategy.average_quality_score,
            confidence=discounted_confidence,
            sample_count=1,
            parent_strategy_id=source_strategy.strategy_id
        )
