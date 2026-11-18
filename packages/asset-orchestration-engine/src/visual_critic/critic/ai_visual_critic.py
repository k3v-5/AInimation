import uuid
from typing import Dict, Any, List
from .critic_schema import CriticReport, CriticIssue, CriticStatus, IssueSeverity
from ..context.evaluation_context import EvaluationContext

class AIVisualCritic:
    """
    AI Visual Critic Engine
    
    Regla Fundamental:
    La IA no dice 'voy a mover este vértice'.
    Dice: 'blade_width debe aumentar aproximadamente un 10% (SET blade_width = 0.055m)'.
    """
    @staticmethod
    def evaluate(context: EvaluationContext, live_measurements: Dict[str, Any]) -> CriticReport:
        issues: List[CriticIssue] = []
        score = 1.0

        # 1. Evaluación de Identidad y Componentes Obligatorios
        actual_comps = live_measurements.get("components", [])
        for comp_name, comp_spec in context.asset_spec.components.items():
            if comp_spec.required and comp_name not in actual_comps:
                issues.append(CriticIssue(
                    issue_id=f"ISSUE-{uuid.uuid4().hex[:4].upper()}",
                    category="COMPONENT",
                    severity=IssueSeverity.CRITICAL,
                    component=comp_name,
                    property_name="existence",
                    current_value=None,
                    expected_value="EXISTS",
                    direction="SET",
                    magnitude=1.0,
                    confidence=0.99,
                    evidence=f"Required component '{comp_name}' is missing from actual asset."
                ))
                score -= 0.50

        # 2. Evaluación de Proporciones (ej. blade_width, blade_length)
        b_dims = live_measurements.get("blade_dimensions", (0.05, 0.02, 0.90))
        act_width = b_dims[0]
        exp_width = context.resolved_parameters.get("blade_width", 0.05)

        # Si el usuario pidió hoja ancha pero la anchura es muy estrecha (< 0.06m)
        if "ancha" in context.asset_spec.original_user_request.lower() and act_width < 0.06:
            issues.append(CriticIssue(
                issue_id=f"ISSUE-{uuid.uuid4().hex[:4].upper()}",
                category="PROPORTION",
                severity=IssueSeverity.MEDIUM,
                component="blade",
                property_name="blade_width",
                current_value=act_width,
                expected_value=0.075,
                direction="INCREASE",
                magnitude=0.075,
                confidence=0.92,
                evidence="User requested 'hoja ancha' but actual blade width is narrow relative to guard."
            ))
            score -= 0.15

        # 3. Determinar Status
        if any(i.severity == IssueSeverity.CRITICAL for i in issues):
            status = CriticStatus.FAIL
        elif len(issues) > 0:
            status = CriticStatus.NEEDS_REVISION
        else:
            status = CriticStatus.PASS

        issues_text = " ".join([i.evidence for i in issues]) if issues else "All constraints satisfied."
        return CriticReport(
            status=status,
            overall_visual_score=max(0.0, round(score, 2)),
            confidence=0.95,
            issues=issues,
            summary=f"Visual critique completed: {len(issues)} issues detected. {issues_text}"
        )
