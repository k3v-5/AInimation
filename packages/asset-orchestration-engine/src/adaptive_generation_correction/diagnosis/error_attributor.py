from typing import Dict, Any, List, Optional
from ..core.adaptive_types import (
    ErrorCategory, CorrectionOp, ScopeLevel, AdaptiveRiskLevel
)
from ..core.adaptive_schema import ErrorDiagnosis, CorrectionCandidate

class ErrorAttributor:
    MAX_DELTA_MAP: Dict[str, float] = {
        "roof_height": 0.40,
        "width": 1.50,
        "roof_pitch": 10.0,
        "window_spacing": 0.50
    }

    @classmethod
    def diagnose_and_attribute(
        cls,
        measured_ratios: Dict[str, float],
        target_ratios: Dict[str, float],
        current_parameters: Dict[str, Any]
    ) -> List[CorrectionCandidate]:
        candidates: List[CorrectionCandidate] = []

        # 1. Error de Proporción de Tejado (Roof Ratio)
        m_roof = measured_ratios.get("roof_ratio", 0.31)
        t_roof = target_ratios.get("roof_ratio", 0.31)
        roof_delta_ratio = m_roof - t_roof

        if abs(roof_delta_ratio) > 0.03:
            curr_h = current_parameters.get("roof_height", 1.80)
            # Reducción o aumento proporcional acotado
            adjustment_factor = t_roof / m_roof if m_roof > 0 else 1.0
            new_h = round(curr_h * adjustment_factor, 2)
            delta = round(new_h - curr_h, 2)
            
            # Limitar delta máximo
            max_d = cls.MAX_DELTA_MAP.get("roof_height", 0.40)
            if abs(delta) > max_d:
                delta = max_d if delta > 0 else -max_d
                new_h = round(curr_h + delta, 2)

            op = CorrectionOp.DECREASE if delta < 0 else CorrectionOp.INCREASE

            candidates.append(CorrectionCandidate(
                candidate_id="CORR_ROOF_HEIGHT",
                parameter="roof_height",
                operation=op,
                old_value=curr_h,
                new_value=new_h,
                delta=delta,
                expected_effect=f"Restore roof ratio from {m_roof:.2f} to target {t_roof:.2f}",
                confidence=0.95,
                cost=1.0,
                scope=ScopeLevel.PARAMETER,
                affected_components=["roof"],
                risk=AdaptiveRiskLevel.LOW
            ))

        # 2. Error de Espaciado de Ventanas
        m_win_spacing = measured_ratios.get("window_spacing", 1.20)
        t_win_spacing = target_ratios.get("window_spacing", 1.20)
        if abs(m_win_spacing - t_win_spacing) > 0.05:
            candidates.append(CorrectionCandidate(
                candidate_id="CORR_WINDOW_SPACING",
                parameter="window_spacing",
                operation=CorrectionOp.SET,
                old_value=m_win_spacing,
                new_value=t_win_spacing,
                delta=round(t_win_spacing - m_win_spacing, 2),
                expected_effect="Align window grid spacing with visual reference",
                confidence=0.92,
                cost=1.0,
                scope=ScopeLevel.COMPONENT,
                affected_components=["windows"],
                risk=AdaptiveRiskLevel.LOW
            ))

        return candidates
