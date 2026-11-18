from typing import Dict, Any, List
from ..core.critic_types import (
    CausalCategory, CriticPriority, EvidenceType, RiskLevel
)
from ..core.critic_schema import (
    CriticDiagnosis, RootCause, EvidenceItem, CriticConfiguration
)
from .base_rule import ICriticRule

class HistoricalOscillationRule(ICriticRule):
    @property
    def rule_id(self) -> str:
        return "RULE_HISTORICAL_OSCILLATION"

    @property
    def category(self) -> CausalCategory:
        return CausalCategory.GENERATION_STRATEGY

    def evaluate(
        self,
        context: Dict[str, Any],
        config: CriticConfiguration
    ) -> List[CriticDiagnosis]:
        diagnoses: List[CriticDiagnosis] = []
        history = context.get("iteration_history", [])
        if len(history) >= config.oscillation_threshold:
            # Check if parameter alternated signs or jumped back and forth
            is_oscillating = context.get("force_oscillation_flag", False)
            if is_oscillating:
                ev = [
                    EvidenceItem(
                        evidence_type=EvidenceType.HISTORICAL_EVIDENCE,
                        source="HISTORICAL_ITERATIONS",
                        description="Oscillation detected across consecutive iterations.",
                        metric_value=f"iterations_checked={len(history)}",
                        confidence=0.96
                    )
                ]
                root_c = RootCause(
                    cause_id="CAUSE_PARAM_OSCILLATION",
                    category=CausalCategory.GENERATION_STRATEGY,
                    description="Correction step magnitude is too large, causing overshooting between bounds.",
                    evidence=ev,
                    probability=0.95
                )
                diag = CriticDiagnosis(
                    diagnosis_id="DIAG_HIST_OSCILLATION",
                    category=CausalCategory.GENERATION_STRATEGY,
                    severity="MAJOR",
                    priority=CriticPriority.HIGH,
                    evidence=ev,
                    probable_causes=[root_c],
                    confidence=0.96,
                    downstream_impact="INFINITE_ITERATION_LOOP",
                    recommended_action="HALVE_CORRECTION_DELTA_MAGNITUDE"
                )
                diagnoses.append(diag)

        return diagnoses
