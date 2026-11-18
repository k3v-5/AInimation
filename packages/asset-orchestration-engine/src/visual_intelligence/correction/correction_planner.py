from typing import Dict, Any, List, Optional
from ..qa.quality_scorer import VerificationReport

class VisualCorrectionPlanner:
    @staticmethod
    def plan_minimal_correction(report: VerificationReport) -> Dict[str, Any]:
        """
        Escalation Ladder:
        PROPERTY -> TRANSFORM -> COMPONENT -> PARAMETRIC -> REBUILD -> REGENERATE
        """
        if report.status == "PASS" and not report.warnings and not report.hard_failures:
            return {"action": "NONE", "message": "Asset satisfies goal specification."}

        actions: List[Dict[str, Any]] = []

        # 1. Proporciones (ej. Hoja corta)
        for fail in report.hard_failures + report.warnings:
            if "BLADE_RATIO" in fail:
                # Escalar únicamente la hoja de forma paramétrica
                actions.append({
                    "type": "PARAMETRIC_SCALE",
                    "target_component": "blade",
                    "target_property": "length",
                    "scale_factor": 1.25,
                    "reason": "Correct blade length ratio to target ~72% of total sword length."
                })
            elif "MATERIAL" in fail or "METALLIC" in fail:
                actions.append({
                    "type": "MODIFY_MATERIAL_PROPERTY",
                    "target_component": "blade",
                    "property": "metallic",
                    "value": 0.90,
                    "reason": "Set blade material to metallic PBR standard."
                })

        if not actions and report.status == "FAIL":
            actions.append({
                "type": "REGENERATE_COMPONENT",
                "target_component": "blade",
                "reason": "Local geometry fundamentally incompatible."
            })

        return {
            "action": "EXECUTE_CORRECTIONS",
            "actions_count": len(actions),
            "actions": actions,
            "preserved_components": ["handle", "guard", "pommel"] # Known good components
        }
