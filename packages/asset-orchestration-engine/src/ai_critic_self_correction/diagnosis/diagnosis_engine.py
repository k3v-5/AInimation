from typing import List, Dict, Any, Optional
from ..core.critic_types import RootCauseSeverity, CriticStatus
from ..core.critic_schema import RootCause

class DiagnosisEngine:
    @staticmethod
    def diagnose_issues(differences: List[Any], confidence: float = 0.95) -> List[RootCause]:
        if not differences:
            return []

        # 1. Comprobar confianza
        if confidence < 0.60:
            return [RootCause(
                cause_id="RC_LOW_CONFIDENCE",
                description="Diagnosis confidence below safety threshold. Human review required.",
                affected_properties=["ALL"],
                confidence=confidence,
                severity=RootCauseSeverity.CRITICAL
            )]

        # 2. Análisis de Causa Raíz (Agrupar síntomas)
        # Síntomas de tejado (altura, chimenea, proporciones)
        roof_symptoms = [d for d in differences if hasattr(d, 'target') and "ROOF" in str(d.target).upper()]
        door_symptoms = [d for d in differences if hasattr(d, 'target') and "DOOR" in str(d.target).upper()]

        causes: List[RootCause] = []

        if roof_symptoms:
            # Agrupa múltiples síntomas de techo en una sola causa raíz
            diff_types = [str(getattr(d, 'diff_type', '')) for d in roof_symptoms]
            is_shape_wrong = any("WRONG_SHAPE" in dt for dt in diff_types)
            severity = RootCauseSeverity.CRITICAL if is_shape_wrong else RootCauseSeverity.HIGH

            causes.append(RootCause(
                cause_id="RC_ROOF_GEOMETRY",
                description="Incorrect roof geometry / proportion affecting roof structure",
                affected_properties=[str(d.target) for d in roof_symptoms],
                evidence=f"{len(roof_symptoms)} interrelated roof symptoms detected ({diff_types})",
                confidence=confidence,
                severity=severity,
                dependencies=["WALL_OPENINGS", "ROOF_SUPPORT"]
            ))

        if door_symptoms:
            causes.append(RootCause(
                cause_id="RC_DOOR_DIMENSION",
                description="Incorrect door width property",
                affected_properties=[str(d.target) for d in door_symptoms],
                evidence="Door width differs from specification",
                confidence=confidence,
                severity=RootCauseSeverity.MEDIUM
            ))

        return causes

class PriorityEngine:
    @staticmethod
    def rank_causes(causes: List[RootCause]) -> List[RootCause]:
        prio_map = {
            RootCauseSeverity.CRITICAL: 0,
            RootCauseSeverity.HIGH: 1,
            RootCauseSeverity.MEDIUM: 2,
            RootCauseSeverity.LOW: 3
        }
        return sorted(causes, key=lambda c: (prio_map.get(c.severity, 4), -c.confidence))
