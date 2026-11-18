from typing import Optional, Dict, Any, Tuple
from ..core.memory_schema import PatternRecord
from ..core.memory_status import PatternStatus

class PatternPromoter:
    @staticmethod
    def record_evidence_and_evaluate(
        pattern: PatternRecord,
        is_success: bool,
        min_trials_to_validate: int = 3,
        min_success_rate: float = 0.80
    ) -> PatternRecord:
        pattern.evidence_count += 1
        if is_success:
            pattern.success_count += 1
            pattern.confidence = min(0.98, round(pattern.confidence + 0.08, 4))
        else:
            pattern.failure_count += 1
            pattern.confidence = max(0.10, round(pattern.confidence - 0.15, 4))

        pattern.success_rate = round(pattern.success_count / pattern.evidence_count, 4)

        # Promoción
        if pattern.status == PatternStatus.CANDIDATE:
            if pattern.evidence_count >= min_trials_to_validate and pattern.success_rate >= min_success_rate:
                pattern.status = PatternStatus.VALIDATED
        elif pattern.status == PatternStatus.VALIDATED:
            if pattern.evidence_count >= 5 and pattern.success_rate >= 0.90:
                pattern.status = PatternStatus.PROMOTED

        return pattern

class NegativeKnowledgeEngine:
    @staticmethod
    def check_failure_region(template_id: str, candidate_params: Dict[str, Any], known_failures: list) -> Tuple[bool, str]:
        for fail in known_failures:
            for p_k, p_v in fail.problematic_parameters.items():
                if p_k in candidate_params:
                    # Comprobar si el valor candidato es igual o superior al umbral problemático
                    if candidate_params[p_k] >= p_v:
                        return True, f"KNOWN_FAILURE_REGION: {p_k}={candidate_params[p_k]} historically produced '{fail.error_type}' in {template_id}."
        return False, "Safe parameter region."
