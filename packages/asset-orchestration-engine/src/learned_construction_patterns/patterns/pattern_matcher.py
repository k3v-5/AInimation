from typing import Dict, Any, List, Optional, Tuple
from ..core.memory_types import PatternState
from ..core.memory_schema import PatternRecord

class PatternMatcher:
    @staticmethod
    def calculate_similarity(pattern: PatternRecord, query: Dict[str, Any]) -> float:
        score = 0.0

        # 1. Familia de Activo (35%)
        q_family = query.get("asset_family", "")
        if q_family and pattern.asset_family.lower() == q_family.lower():
            score += 0.35
        elif not q_family:
            score += 0.15

        # 2. Firma del Problema (35%)
        q_prob = query.get("problem_signature", "")
        if q_prob and pattern.problem_signature == q_prob:
            score += 0.35
        elif not q_prob:
            score += 0.15

        # 3. Compatibilidad de Versión (15%)
        q_builder_ver = query.get("builder_version", "v1.0.0")
        if pattern.builder_version == q_builder_ver:
            score += 0.15

        # 4. Confianza y Calidad Histórica (15%)
        score += (pattern.confidence * 0.10) + (pattern.quality * 0.05)

        return round(min(1.00, score), 4)

    @classmethod
    def search_and_rank(
        cls,
        patterns: List[PatternRecord],
        query: Dict[str, Any],
        top_k: int = 5
    ) -> List[Tuple[PatternRecord, float, str]]:
        results: List[Tuple[PatternRecord, float, str]] = []

        q_builder_ver = query.get("builder_version", "v1.0.0")

        for p in patterns:
            # Filtro duro: descartar invalidados
            if p.state == PatternState.INVALIDATED or p.state == PatternState.DEPRECATED:
                continue

            # Filtro duro: compatibilidad de versión del builder
            if p.builder_version != q_builder_ver:
                continue

            sim = cls.calculate_similarity(p, query)
            if sim >= 0.50:
                explanation = (
                    f"Selected because: asset family '{p.asset_family}' matches, "
                    f"problem signature '{p.problem_signature}' matches, "
                    f"{sim*100:.0f}% similarity score, {p.success_count}/{p.applications_count} historical successes."
                )
                results.append((p, sim, explanation))

        # Ordenar deterministamente de mayor a menor puntuación
        results.sort(key=lambda item: (item[1], item[0].confidence, item[0].success_rate), reverse=True)
        return results[:top_k]

    @staticmethod
    def detect_conflicts(pattern_a: PatternRecord, pattern_b: PatternRecord) -> Tuple[bool, str]:
        if pattern_a.target_parameter == pattern_b.target_parameter:
            # Misma variable pero con signos o magnitudes divergentes
            if (pattern_a.correction_delta > 0 and pattern_b.correction_delta < 0) or \
               (pattern_a.correction_delta < 0 and pattern_b.correction_delta > 0) or \
               abs(pattern_a.correction_delta - pattern_b.correction_delta) > 0.05:
                return True, f"CONFLICT_DETECTED: Pattern '{pattern_a.name}' (delta: {pattern_a.correction_delta:+.2f}) conflicts with Pattern '{pattern_b.name}' (delta: {pattern_b.correction_delta:+.2f}) on parameter '{pattern_a.target_parameter}'."

        return False, "No conflict."
