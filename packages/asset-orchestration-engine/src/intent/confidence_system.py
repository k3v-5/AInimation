from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional

class ConfidenceAction(str, Enum):
    ALLOW = "ALLOW"                  # Confianza >= threshold_allow
    REQUIRE_VALIDATION = "VALIDATE"  # threshold_clarify <= Confianza < threshold_allow
    REQUIRE_CLARIFICATION = "CLARIFY"# Confianza < threshold_clarify

@dataclass
class ConfidenceThresholds:
    allow_threshold: float = 0.90
    clarify_threshold: float = 0.70

class ConfidenceSystem:
    def __init__(self, thresholds: Optional[ConfidenceThresholds] = None):
        self.thresholds = thresholds or ConfidenceThresholds()

    def evaluate(self, confidence: float) -> Tuple[ConfidenceAction, str]:
        if confidence >= self.thresholds.allow_threshold:
            return ConfidenceAction.ALLOW, "Confidence is sufficient to proceed deterministically."
        elif confidence >= self.thresholds.clarify_threshold:
            return ConfidenceAction.REQUIRE_VALIDATION, "Confidence is moderate; plan validation required before execution."
        else:
            return ConfidenceAction.REQUIRE_CLARIFICATION, "Confidence is low; explicit clarification required from user."
