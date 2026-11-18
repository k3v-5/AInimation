from typing import List
from ..core.scoring_schema import (
    QualityReport, QualityResult, AcceptanceExplanation,
    QualityMetric, QualityDefect
)

class QualityReportGenerator:
    @classmethod
    def generate_report(
        cls,
        report_id: str,
        asset_id: str,
        semantic_id: str,
        result: QualityResult,
        explanation: AcceptanceExplanation,
        metrics: List[QualityMetric],
        defects: List[QualityDefect],
        profile_id: str
    ) -> QualityReport:
        lines = [
            "==================================================================",
            f"  ASSET QUALITY & ACCEPTANCE REPORT: [{asset_id}]",
            "==================================================================",
            f"Quality Score: {result.overall_score:.1f}/100.0  |  Status: {result.acceptance_status.value}  |  Level: {result.quality_level.value}",
            f"Profile: {profile_id}  |  Evaluation ID: {result.evaluation_id}",
            "------------------------------------------------------------------",
            "Category Scores Breakdown:"
        ]
        for cat, score in result.category_scores.items():
            if cat != "OVERALL":
                lines.append(f"  - {cat:<20}: {score:.1f}%")

        lines.append("------------------------------------------------------------------")
        if result.blocking_reasons:
            lines.append("Blocking Reasons:")
            for b in result.blocking_reasons:
                lines.append(f"  [X] {b}")
        else:
            lines.append("Blocking Reasons: None")

        if explanation.warnings:
            lines.append("Warnings:")
            for w in explanation.warnings:
                lines.append(f"  [!] {w}")

        lines.append("==================================================================")
        human_text = "\n".join(lines)

        return QualityReport(
            report_id=report_id,
            asset_id=asset_id,
            semantic_id=semantic_id,
            quality_result=result,
            explanation=explanation,
            metrics=metrics,
            defects=defects,
            profile_id=profile_id,
            human_readable=human_text
        )
