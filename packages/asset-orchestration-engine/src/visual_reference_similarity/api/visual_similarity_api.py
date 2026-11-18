from typing import Dict, Any, List, Optional
from ..core.similarity_types import (
    ReferenceType, ReferencePriority, ReferenceCategory, EvaluationStatus,
    DifferenceType, DifferenceSeverity, CorrectionPriority, ViewDirection
)
from ..core.similarity_schema import (
    ReferenceProfile, AssetObservation, DifferenceRecord, CorrectionRequest,
    SimilarityWeights, SimilarityReport, CandidateAsset
)
from ..analyzer.reference_analyzer import ReferenceAnalyzer, AssetObserver
from ..engine.similarity_engine import SimilarityEngine
from ..engine.loop_diagnostics import LoopDiagnostics

class VisualSimilarityAPI:
    """
    Visual Reference & Similarity System API (AOE v36)
    
    Regla Fundamental:
    LA IA NO ES JUEZ DE SU PROPIO RESULTADO BASÁNDOSE ÚNICAMENTE EN TEXTO.
    COMPARA OBSERVACIONES GEOMÉTRICAS Y VISUALES CONTRA PERFILES DE REFERENCIA,
    GENERA INFORMES CON PUNTUACIONES CUANTIFICABLES POR CATEGORÍA,
    APLICA PUERTAS DE FALLO CRÍTICO Y EMITE SOLICITUDES DE CORRECCIÓN (CorrectionRequest).
    """
    def __init__(self):
        self.evaluation_cache: Dict[str, SimilarityReport] = {}

    def create_reference_profile(
        self,
        ref_id: str,
        expected_features: Dict[str, Any],
        proportions: Optional[Dict[str, float]] = None,
        applies_to: Optional[List[str]] = None,
        priority: ReferencePriority = ReferencePriority.HIGH
    ) -> ReferenceProfile:
        return ReferenceAnalyzer.create_profile(ref_id, expected_features, proportions, applies_to, priority)

    def observe_asset(
        self,
        asset_id: str,
        detected_features: Dict[str, Any],
        detected_proportions: Optional[Dict[str, float]] = None,
        aspect_ratio: float = 1.3
    ) -> AssetObservation:
        return AssetObserver.observe(asset_id, detected_features, detected_proportions, aspect_ratio)

    def evaluate_asset(
        self,
        ref: ReferenceProfile,
        obs: AssetObservation,
        weights: Optional[SimilarityWeights] = None,
        use_cache: bool = True
    ) -> SimilarityReport:
        cache_key = f"{ref.reference_id}_{obs.asset_id}_{hash(str(obs.detected_features))}"
        if use_cache and cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]

        report = SimilarityEngine.evaluate(ref, obs, weights)
        if use_cache:
            self.evaluation_cache[cache_key] = report
        return report

    def detect_conflicts(self, ref_a: ReferenceProfile, ref_b: ReferenceProfile):
        return ReferenceAnalyzer.detect_conflicts(ref_a, ref_b)

    def detect_oscillation(self, history: List[float]) -> bool:
        return LoopDiagnostics.detect_oscillation(history)

    def detect_stagnation(self, scores: List[float], patience: int = 3) -> bool:
        return LoopDiagnostics.detect_stagnation(scores, patience)

    def detect_regression(self, prev_report: SimilarityReport, new_report: SimilarityReport) -> bool:
        return LoopDiagnostics.detect_regression(prev_report, new_report)

    def rank_candidates(self, candidates: List[CandidateAsset]) -> List[CandidateAsset]:
        return LoopDiagnostics.rank_candidates(candidates)
