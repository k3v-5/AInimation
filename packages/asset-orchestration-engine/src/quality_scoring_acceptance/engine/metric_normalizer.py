from typing import Any
from ..core.scoring_types import DirectionType

class MetricNormalizer:
    @classmethod
    def normalize(cls, raw_val: Any, direction: DirectionType) -> float:
        if direction == DirectionType.BOOLEAN:
            return 1.0 if bool(raw_val) else 0.0

        if isinstance(raw_val, (int, float)):
            val = float(raw_val)
            if direction == DirectionType.HIGHER_IS_BETTER:
                # Assuming raw_val is either 0..1 or 0..100
                if val > 1.0:
                    val = val / 100.0
                return max(0.0, min(1.0, val))
            elif direction == DirectionType.LOWER_IS_BETTER:
                # 0 error is 1.0 score
                if val > 1.0:
                    val = val / 100.0
                return max(0.0, min(1.0, 1.0 - val))
            elif direction == DirectionType.RANGE_TARGET:
                # 1.0 is exact target
                diff = abs(1.0 - val)
                return max(0.0, min(1.0, 1.0 - diff))

        return 1.0
