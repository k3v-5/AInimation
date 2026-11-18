from .core.similarity_types import (
    ReferenceType, ReferencePriority, ReferenceCategory, EvaluationStatus,
    DifferenceType, DifferenceSeverity, CorrectionPriority, ViewDirection
)
from .core.similarity_schema import (
    ReferenceProfile, AssetObservation, DifferenceRecord, CorrectionRequest,
    SimilarityWeights, SimilarityReport, CandidateAsset
)
from .analyzer.reference_analyzer import ReferenceAnalyzer, AssetObserver
from .engine.difference_detector import DifferenceDetector
from .engine.similarity_engine import SimilarityEngine, CorrectionGenerator
from .engine.loop_diagnostics import LoopDiagnostics
from .api.visual_similarity_api import VisualSimilarityAPI

__all__ = [
    "ReferenceType",
    "ReferencePriority",
    "ReferenceCategory",
    "EvaluationStatus",
    "DifferenceType",
    "DifferenceSeverity",
    "CorrectionPriority",
    "ViewDirection",
    "ReferenceProfile",
    "AssetObservation",
    "DifferenceRecord",
    "CorrectionRequest",
    "SimilarityWeights",
    "SimilarityReport",
    "CandidateAsset",
    "ReferenceAnalyzer",
    "AssetObserver",
    "DifferenceDetector",
    "SimilarityEngine",
    "CorrectionGenerator",
    "LoopDiagnostics",
    "VisualSimilarityAPI"
]
