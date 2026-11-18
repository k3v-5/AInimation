from typing import List, Tuple
from ..core.readiness_types import ReadinessStatus, ValidationSeverity
from ..core.readiness_schema import EngineValidationResult, EngineReadinessScore

class ReadinessEvaluator:
    @classmethod
    def evaluate(
        cls,
        validation_results: List[EngineValidationResult]
    ) -> Tuple[ReadinessStatus, EngineReadinessScore, List[str], List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []

        for r in validation_results:
            if not r.passed:
                if r.severity == ValidationSeverity.BLOCKER:
                    blockers.append(f"[{r.target}] {r.message}")
                elif r.severity == ValidationSeverity.WARNING:
                    warnings.append(f"[{r.target}] {r.message}")

        if len(blockers) > 0:
            status = ReadinessStatus.NOT_READY
            score_val = 50.0
        elif len(warnings) > 0:
            status = ReadinessStatus.READY_WITH_WARNINGS
            score_val = 90.0
        else:
            status = ReadinessStatus.READY
            score_val = 100.0

        score = EngineReadinessScore(
            geometry=score_val,
            materials=score_val,
            textures=score_val,
            uv=score_val,
            transforms=score_val,
            collision=score_val,
            lod=score_val,
            total=score_val
        )

        return status, score, blockers, warnings
