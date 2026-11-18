# Phase 25 exports
from .core.reference_schema import (
    LandmarkFeature, ProportionFeature, GeometricDiscrepancy,
    ReferenceProfile, ErrorMap
)
from .analysis.feature_extractor import FeatureExtractor
from .matching.geometric_matcher import GeometricMatcher
from .api.visual_reference_api import VisualReferenceAPI

# Phase 41 exports
from .core.critic_types import (
    EvaluationMode, VisualDiagnosisType, CriticDecisionType,
    ReferenceRole, EvaluationStage, ColorSpaceType
)
from .core.critic_schema import (
    ReferenceImageSpec, SilhouetteMetrics, ProportionMetrics,
    MaterialMetrics, VisualDiagnosis, ParameterCorrection,
    ScoringWeights, VisualScoreReport
)
from .analyzers.silhouette_analyzer import SilhouetteAnalyzer, ProportionAnalyzer, MaterialAnalyzer
from .diagnostic.diagnostic_engine import DiagnosticEngine, ParameterCorrectionEngine
from .engine.visual_reference_matcher import VisualReferenceMatcher
from .api.visual_reference_matcher_api import VisualReferenceMatcherAPI

__all__ = [
    # Phase 25
    "LandmarkFeature",
    "ProportionFeature",
    "GeometricDiscrepancy",
    "ReferenceProfile",
    "ErrorMap",
    "FeatureExtractor",
    "GeometricMatcher",
    "VisualReferenceAPI",
    # Phase 41
    "EvaluationMode",
    "VisualDiagnosisType",
    "CriticDecisionType",
    "ReferenceRole",
    "EvaluationStage",
    "ColorSpaceType",
    "ReferenceImageSpec",
    "SilhouetteMetrics",
    "ProportionMetrics",
    "MaterialMetrics",
    "VisualDiagnosis",
    "ParameterCorrection",
    "ScoringWeights",
    "VisualScoreReport",
    "SilhouetteAnalyzer",
    "ProportionAnalyzer",
    "MaterialAnalyzer",
    "DiagnosticEngine",
    "ParameterCorrectionEngine",
    "VisualReferenceMatcher",
    "VisualReferenceMatcherAPI"
]
