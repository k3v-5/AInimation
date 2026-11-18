import uuid
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from ..critic.critic_schema import CriticReport, CriticIssue

@dataclass
class ParameterPatch:
    patch_id: str
    target_component: str
    parameter_name: str
    operation: str # SET, INCREASE, DECREASE
    value: Any
    reason: str
    confidence: float

class ParameterPatchGenerator:
    @staticmethod
    def generate_patches(report: CriticReport, protected_parameters: List[str] = None) -> List[ParameterPatch]:
        patches: List[ParameterPatch] = []
        protected = protected_parameters or []

        for issue in report.issues:
            # Si el parámetro está protegido por override de usuario, no modificar
            if issue.property_name in protected:
                continue

            if issue.category == "PROPORTION" and issue.property_name:
                patches.append(ParameterPatch(
                    patch_id=f"patch_{uuid.uuid4().hex[:6]}",
                    target_component=issue.component,
                    parameter_name=issue.property_name,
                    operation=issue.direction,
                    value=issue.expected_value or issue.magnitude,
                    reason=issue.evidence,
                    confidence=issue.confidence
                ))

        return patches
