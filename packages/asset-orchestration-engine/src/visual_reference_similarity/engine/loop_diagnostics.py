from typing import List
from ..core.similarity_schema import SimilarityReport, CandidateAsset

class LoopDiagnostics:
    @staticmethod
    def detect_oscillation(history: List[float]) -> bool:
        """
        Detecta oscilación si los valores alternan subida y bajada repetidamente.
        Ejemplo: [0.70, 0.40, 0.70, 0.40]
        """
        if len(history) < 4:
            return False

        deltas = [history[i+1] - history[i] for i in range(len(history)-1)]
        signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in deltas]

        # Comprobar si alterna signos constantemente: + - + o - + -
        for i in range(len(signs) - 2):
            if signs[i] != 0 and signs[i] == -signs[i+1] and signs[i+1] == -signs[i+2]:
                return True
        return False

    @staticmethod
    def detect_stagnation(scores: List[float], patience: int = 3) -> bool:
        """
        Detecta si no ha habido mejora durante N iteraciones consecutivas.
        """
        if len(scores) < patience:
            return False

        recent = scores[-patience:]
        return all(recent[i] <= recent[0] for i in range(1, len(recent)))

    @staticmethod
    def detect_regression(prev_report: SimilarityReport, new_report: SimilarityReport) -> bool:
        """
        Detecta regresión si una categoría crítica empeora significativamente.
        """
        for cat in ["silhouette", "proportions"]:
            prev_cat = prev_report.category_scores.get(cat, 1.0)
            new_cat = new_report.category_scores.get(cat, 1.0)
            if new_cat < prev_cat - 0.15:
                return True
        return False

    @staticmethod
    def rank_candidates(candidates: List[CandidateAsset]) -> List[CandidateAsset]:
        """
        Ordena candidatos priorizando cero fallos críticos y luego por puntuación global descendente.
        """
        return sorted(
            candidates,
            key=lambda c: (c.critical_failures_count, -c.score)
        )
