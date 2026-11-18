from typing import Dict, Any, Optional
from ..core.failure_types import FailureType
from ..core.severity import FailureSeverity
from .category_rules import CategoryRules
from ..capture.exception_normalizer import ExceptionNormalizer

class FailureClassifier:
    """Classifies raw errors, benchmarks, and operational failures into deterministic FailureTypes."""
    
    @classmethod
    def classify(cls, message: str, evidence: Optional[Dict[str, Any]] = None) -> FailureType:
        if evidence:
            f_type_from_ev = CategoryRules.classify_from_evidence(evidence)
            if f_type_from_ev != FailureType.UNKNOWN:
                return f_type_from_ev

        f_type, _, _, _ = ExceptionNormalizer.normalize(message)
        return f_type
