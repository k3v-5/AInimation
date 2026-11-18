from .core.evaluation_types import (
    EvaluationCategory, DefectType, DefectSeverity,
    DefectCauseCategory, AcceptanceStatus, EvaluationLevel,
    RegressionStatus
)
from .core.evaluation_schema import (
    VisualDefect, CorrectionHint, CategoryEvaluation,
    RegionEvaluation, RequirementEvaluationResult, EvaluationDelta,
    EvaluationConfiguration, VisualEvaluationResult, EvaluationValidationResult
)
from .metrics.base_metric import IVisualMetric
from .metrics.silhouette_metric import SilhouetteMetric
from .metrics.proportion_metric import ProportionMetric
from .metrics.color_material_metric import ColorMaterialMetric
from .metrics.lighting_metric import LightingMetric
from .metrics.metric_registry import MetricRegistry
from .engine.defect_detector import DefectDetector
from .engine.temporal_comparator import TemporalComparator
from .engine.evaluation_hasher import EvaluationHasher
from .engine.automated_visual_evaluation_engine import AutomatedVisualEvaluationEngine
from .api.automated_visual_evaluation_api import AutomatedVisualEvaluationAPI

__all__ = [
    "EvaluationCategory",
    "DefectType",
    "DefectSeverity",
    "DefectCauseCategory",
    "AcceptanceStatus",
    "EvaluationLevel",
    "RegressionStatus",
    "VisualDefect",
    "CorrectionHint",
    "CategoryEvaluation",
    "RegionEvaluation",
    "RequirementEvaluationResult",
    "EvaluationDelta",
    "EvaluationConfiguration",
    "VisualEvaluationResult",
    "EvaluationValidationResult",
    "IVisualMetric",
    "SilhouetteMetric",
    "ProportionMetric",
    "ColorMaterialMetric",
    "LightingMetric",
    "MetricRegistry",
    "DefectDetector",
    "TemporalComparator",
    "EvaluationHasher",
    "AutomatedVisualEvaluationEngine",
    "AutomatedVisualEvaluationAPI"
]
