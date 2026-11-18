from typing import Dict, Any, List
from .quality_gate import QualityStatus
from ..diagnosis.difference_detector import DifferenceRecord
from ..diagnosis.correction_mapper import CorrectionProposal

class ReportGenerator:
    @staticmethod
    def generate_json_report(
        asset_id: str,
        status: QualityStatus,
        quality_score: float,
        silhouette_score: float,
        dimension_score: float,
        structural_score: float,
        differences: List[DifferenceRecord],
        corrections: List[CorrectionProposal],
        unaffected_components: List[str]
    ) -> Dict[str, Any]:
        return {
            "asset_id": asset_id,
            "status": status.value,
            "quality_score": quality_score,
            "scores": {
                "silhouette": silhouette_score,
                "dimensions": dimension_score,
                "structure": structural_score
            },
            "differences_count": len(differences),
            "differences": [
                {
                    "target": d.target_component,
                    "type": d.diff_type.value,
                    "severity": d.severity,
                    "confidence": d.confidence,
                    "current": d.current_value,
                    "expected": d.expected_value,
                    "message": d.message
                }
                for d in differences
            ],
            "corrections": [
                {
                    "target": c.target_component,
                    "parameter": c.parameter,
                    "operation": c.operation,
                    "value": c.value,
                    "reason": c.reason
                }
                for c in corrections
            ],
            "unaffected_components": unaffected_components
        }

    @staticmethod
    def generate_human_readable_report(json_report: Dict[str, Any]) -> str:
        lines = [
            f"Visual QA Report: {json_report['asset_id']}",
            f"Status: {json_report['status']} (Quality Score: {round(json_report['quality_score'] * 100, 1)}%)",
            "--------------------------------------------------",
            "Scores Breakdown:",
            f" - Silhouette: {round(json_report['scores']['silhouette'] * 100, 1)}%",
            f" - Dimensions: {round(json_report['scores']['dimensions'] * 100, 1)}%",
            f" - Structure:  {round(json_report['scores']['structure'] * 100, 1)}%",
            ""
        ]

        if json_report["differences"]:
            lines.append("Detected Differences:")
            for d in json_report["differences"]:
                lines.append(f" * [{d['type']}] {d['message']}")
            lines.append("")

        if json_report["corrections"]:
            lines.append("Suggested Parametric Corrections:")
            for c in json_report["corrections"]:
                lines.append(f" -> {c['target']}.{c['parameter']} = {c['value']} ({c['reason']})")
            lines.append("")

        if json_report["unaffected_components"]:
            lines.append(f"Unaffected (Clean) Components: {', '.join(json_report['unaffected_components'])}")

        return "\n".join(lines)
