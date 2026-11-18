from typing import List
from ..core.readiness_schema import (
    EngineReadinessManifest, EngineValidationResult, EngineReadinessScore
)
from ..core.readiness_types import ReadinessStatus

class ReadinessManifestGenerator:
    @classmethod
    def generate_manifest(
        cls,
        asset_id: str,
        semantic_id: str,
        readiness_status: ReadinessStatus,
        readiness_score: EngineReadinessScore,
        validation_results: List[EngineValidationResult],
        engine_profile_id: str
    ) -> EngineReadinessManifest:
        return EngineReadinessManifest(
            manifest_id=f"MANIFEST_READY_{asset_id}",
            asset_id=asset_id,
            semantic_id=semantic_id,
            readiness_status=readiness_status,
            readiness_score=readiness_score,
            validation_results=validation_results,
            preparation_operations=[],
            engine_profile_id=engine_profile_id
        )

    @classmethod
    def format_human_report(cls, manifest: EngineReadinessManifest) -> str:
        lines = [
            "==================================================================",
            f"  GAME-ENGINE READINESS REPORT: [{manifest.asset_id}]",
            "==================================================================",
            f"Status: {manifest.readiness_status.value}  |  Score: {manifest.readiness_score.total:.1f}/100.0",
            f"Target Engine Profile: {manifest.engine_profile_id}",
            "------------------------------------------------------------------",
            "Checks Summary:"
        ]
        for v in manifest.validation_results:
            icon = "[PASS]" if v.passed else f"[{v.severity.value}]"
            lines.append(f"  {icon} {v.validator_id:<25}: {v.message}")
        lines.append("==================================================================")
        return "\n".join(lines)
