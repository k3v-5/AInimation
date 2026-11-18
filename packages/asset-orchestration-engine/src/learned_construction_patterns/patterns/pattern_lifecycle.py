from ..core.memory_types import PatternState
from ..core.memory_schema import PatternRecord

class PatternLifecycleManager:
    PROMOTION_THRESHOLD_VALIDATED = 3
    PROMOTION_THRESHOLD_KNOWN_GOOD = 5
    INVALIDATION_FAILURE_LIMIT = 3

    @classmethod
    def record_success(cls, pattern: PatternRecord, improvement: float = 0.15):
        pattern.applications_count += 1
        pattern.success_count += 1
        pattern.success_rate = round(pattern.success_count / pattern.applications_count, 3)
        pattern.confidence = round(min(0.99, pattern.confidence + 0.03), 3)

        # Actualizar media móvil de mejora
        pattern.average_improvement = round(
            (pattern.average_improvement * (pattern.success_count - 1) + improvement) / pattern.success_count, 3
        )

        # Promoción de estado
        if pattern.success_count >= cls.PROMOTION_THRESHOLD_KNOWN_GOOD:
            pattern.state = PatternState.KNOWN_GOOD
        elif pattern.success_count >= cls.PROMOTION_THRESHOLD_VALIDATED:
            pattern.state = PatternState.VALIDATED
        else:
            pattern.state = PatternState.CANDIDATE

    @classmethod
    def record_failure(cls, pattern: PatternRecord):
        pattern.applications_count += 1
        pattern.failure_count += 1
        pattern.success_rate = round(pattern.success_count / pattern.applications_count, 3)
        pattern.confidence = round(max(0.10, pattern.confidence - 0.20), 3)

        if pattern.failure_count >= cls.INVALIDATION_FAILURE_LIMIT or pattern.confidence <= 0.40:
            pattern.state = PatternState.INVALIDATED
