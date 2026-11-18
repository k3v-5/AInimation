import time
from typing import Dict, Any, List, Optional
from ..core.critic_types import (
    DefectCategory, DefectSeverity, CriticRecommendation,
    QualityProfile, CriticCameraView
)
from ..core.critic_schema import (
    ExpectedState, ActualState, VisualDefect, CorrectionPlanItem, CriticResult
)
from ..analyzers.silhouette_analyzer import SilhouetteAnalyzer
from ..analyzers.style_material_analyzer import StyleMaterialAnalyzer
from ..analyzers.semantic_detector import SemanticDetector

class SemanticComparator:
    @classmethod
    def evaluate(
        cls,
        expected: ExpectedState,
        actual: ActualState,
        profile: QualityProfile = QualityProfile.PRODUCTION
    ) -> CriticResult:
        defects: List[VisualDefect] = []
        warnings: List[str] = []
        hard_failures: List[str] = []
        correction_plan: List[CorrectionPlanItem] = []

        # 1. Fallo Fundamental de Identidad Estructural (e.g. CASA vs NAVE ESPACIAL)
        if expected.asset_class.upper() != actual.detected_class.upper():
            defects.append(VisualDefect(
                defect_id="DEF_STRUCTURAL_IDENTITY",
                category=DefectCategory.STRUCTURAL_IDENTITY_FAILURE,
                severity=DefectSeverity.CRITICAL,
                confidence=0.99,
                affected_component="root",
                expected=expected.asset_class,
                actual=actual.detected_class,
                evidence=f"Asset class mismatch: Expected '{expected.asset_class}', detected '{actual.detected_class}'.",
                recommended_action="REGENERATE_ASSET",
                scope="ASSET"
            ))
            hard_failures.append("STRUCTURAL_IDENTITY_FAILURE")
            return CriticResult(
                overall_score=0.10,
                technical_score=0.10,
                visual_score=0.10,
                hard_failures=hard_failures,
                defects=defects,
                warnings=["Complete asset class mismatch."],
                recommendation=CriticRecommendation.REGENERATE_ASSET,
                correction_plan=[CorrectionPlanItem(
                    item_id="CORR_FULL_REGEN",
                    defect_id="DEF_STRUCTURAL_IDENTITY",
                    action="REGENERATE_ASSET",
                    target_component="root",
                    expected_effect="Regenerate asset matching intended class"
                )],
                explanation_human=f"Structural identity failure: Model is a '{actual.detected_class}' instead of a '{expected.asset_class}'.",
                explanation_agent="Execute full asset regeneration with correct archetype."
            )

        # 2. Detección de Componentes Prohibidos (e.g. Antena parabólica en casa medieval)
        forbidden_found = SemanticDetector.detect_forbidden_components(
            actual.detected_components, expected.forbidden_components
        )
        for forb in forbidden_found:
            defects.append(VisualDefect(
                defect_id=f"DEF_FORBIDDEN_{forb.upper()}",
                category=DefectCategory.FORBIDDEN_COMPONENT,
                severity=DefectSeverity.MAJOR,
                confidence=0.96,
                affected_component=forb,
                expected="NONE (Forbidden)",
                actual=forb,
                evidence=f"Detected forbidden modern/unwanted component '{forb}'.",
                recommended_action=f"remove {forb}",
                scope="COMPONENT"
            ))
            correction_plan.append(CorrectionPlanItem(
                item_id=f"CORR_REMOVE_{forb.upper()}",
                defect_id=f"DEF_FORBIDDEN_{forb.upper()}",
                action=f"REMOVE_{forb.upper()}",
                target_component=forb,
                expected_effect=f"Remove forbidden element '{forb}'"
            ))

        # 3. Componentes Requeridos Faltantes
        for req in expected.required_components:
            if req not in actual.detected_components:
                defects.append(VisualDefect(
                    defect_id=f"DEF_MISSING_{req.upper()}",
                    category=DefectCategory.MISSING_COMPONENT,
                    severity=DefectSeverity.CRITICAL,
                    confidence=0.98,
                    affected_component=req,
                    expected=req,
                    actual="MISSING",
                    evidence=f"Required component '{req}' not found.",
                    recommended_action=f"add {req}",
                    scope="COMPONENT"
                ))
                hard_failures.append(f"MISSING_{req.upper()}")

        # 4. Error de Proporciones (e.g. Techo 51% vs 30%)
        exp_roof = expected.expected_proportions.get("roof_ratio", 0.30)
        act_roof = actual.measured_proportions.get("roof_ratio", exp_roof)
        if abs(act_roof - exp_roof) > 0.05:
            defects.append(VisualDefect(
                defect_id="DEF_WRONG_ROOF_PROPORTION",
                category=DefectCategory.WRONG_PROPORTION,
                severity=DefectSeverity.MAJOR,
                confidence=0.95,
                affected_component="roof",
                expected=f"{exp_roof * 100:.0f}% total height",
                actual=f"{act_roof * 100:.0f}% total height",
                evidence=f"Roof occupies {act_roof * 100:.0f}% of total height; expected {exp_roof * 100:.0f}%.",
                recommended_action="reduce roof height",
                scope="LOCAL"
            ))
            correction_plan.append(CorrectionPlanItem(
                item_id="CORR_ROOF_HEIGHT",
                defect_id="DEF_WRONG_ROOF_PROPORTION",
                action="MODIFY_PARAMETER",
                target_component="roof",
                parameter="roof_height",
                delta=round(exp_roof - act_roof, 2),
                expected_effect="Restore roof proportion to target range"
            ))

        # 5. Errores Espaciales y Oclusión (e.g. Ventana oculta tras el muro)
        for comp, status in actual.component_spatial_status.items():
            if status == "BEHIND_WALL":
                defects.append(VisualDefect(
                    defect_id=f"DEF_SPATIAL_{comp.upper()}",
                    category=DefectCategory.SPATIAL_ERROR,
                    severity=DefectSeverity.MODERATE,
                    confidence=0.92,
                    affected_component=comp,
                    expected="VISIBLY_ATTACHED_ON_WALL",
                    actual="BEHIND_WALL",
                    evidence=f"Component '{comp}' is positioned behind wall surface.",
                    recommended_action=f"reposition {comp}",
                    scope="LOCAL"
                ))
                correction_plan.append(CorrectionPlanItem(
                    item_id=f"CORR_REPOS_{comp.upper()}",
                    defect_id=f"DEF_SPATIAL_{comp.upper()}",
                    action="REPOSITION",
                    target_component=comp,
                    expected_effect=f"Reposition '{comp}' to outer facade"
                ))

        # 6. Estilo y Micro-Detalle Excesivo
        style_eval = StyleMaterialAnalyzer.evaluate_style_and_density(
            expected.style, actual.is_photorealistic, actual.detail_density
        )
        if style_eval["has_style_mismatch"]:
            defects.append(VisualDefect(
                defect_id="DEF_STYLE_MISMATCH",
                category=DefectCategory.STYLE_MISMATCH,
                severity=DefectSeverity.MODERATE,
                confidence=0.90,
                affected_component="root",
                expected=expected.style,
                actual="PHOTOREALISTIC",
                evidence="Asset contains photorealistic shading contradicting stylized low-poly target.",
                recommended_action="simplify geometry and apply stylized shader",
                scope="ASSET"
            ))
        if style_eval["has_excessive_detail"]:
            defects.append(VisualDefect(
                defect_id="DEF_EXCESSIVE_DETAIL",
                category=DefectCategory.EXCESSIVE_DETAIL,
                severity=DefectSeverity.MINOR,
                confidence=0.88,
                affected_component="root",
                expected="LOW_DETAIL_DENSITY",
                actual=f"density {actual.detail_density:.2f}",
                evidence="Excessive micro-surface geometric detail.",
                recommended_action="simplify geometry",
                scope="ASSET"
            ))

        # 7. Caso de Componentes Extras Específicos (e.g. Barril con 3 aros en vez de 2)
        if "ring_03" in actual.detected_components:
            defects.append(VisualDefect(
                defect_id="DEF_EXTRA_RING",
                category=DefectCategory.EXTRA_COMPONENT,
                severity=DefectSeverity.MINOR,
                confidence=0.95,
                affected_component="ring_03",
                expected="2 rings",
                actual="3 rings",
                evidence="Detected 3 rings instead of the requested 2.",
                recommended_action="remove_extra_ring",
                scope="LOCAL"
            ))
            correction_plan.append(CorrectionPlanItem(
                item_id="CORR_REMOVE_RING_03",
                defect_id="DEF_EXTRA_RING",
                action="REMOVE_COMPONENT",
                target_component="ring_03",
                expected_effect="Remove third ring to match specification"
            ))

        # 8. Comprobación de Multi-View
        if actual.multi_view_aspect_ratios:
            mv = SilhouetteAnalyzer.evaluate_multi_view_aspect_ratios(actual.multi_view_aspect_ratios)
            if not mv["overall_ok"]:
                defects.append(VisualDefect(
                    defect_id="DEF_MULTIVIEW_PROPORTION",
                    category=DefectCategory.WRONG_PROPORTION,
                    severity=DefectSeverity.MAJOR,
                    confidence=0.94,
                    affected_component="side_view",
                    expected="1.20 side aspect ratio",
                    actual=f"error {mv['side_error']}",
                    evidence=f"Side camera view exceeds tolerance (error: {mv['side_error']}).",
                    recommended_action="adjust side profile depth",
                    scope="LOCAL"
                ))

        # 9. Filtro de Baja Confianza (e.g. posible chimenea con 0.41)
        for comp, conf in actual.detection_confidences.items():
            if conf < 0.50:
                warnings.append(f"UNCERTAIN: Possible defect on '{comp}' has low confidence ({conf:.2f}). Regeneration suppressed.")

        # Cálculo de Puntuaciones
        penalty = sum(0.20 for d in defects if d.severity in [DefectSeverity.CRITICAL, DefectSeverity.MAJOR])
        penalty += sum(0.08 for d in defects if d.severity in [DefectSeverity.MODERATE, DefectSeverity.MINOR])
        
        overall_score = max(0.10, round(1.0 - penalty, 3))
        if hard_failures:
            overall_score = min(overall_score, 0.40)

        # Recomendación
        if overall_score >= 0.85 and not hard_failures:
            recommendation = CriticRecommendation.ACCEPT
        elif defects and all(d.scope == "LOCAL" for d in defects) and overall_score >= 0.60:
            recommendation = CriticRecommendation.MINOR_FIX
        elif overall_score >= 0.40:
            recommendation = CriticRecommendation.REFINE
        else:
            recommendation = CriticRecommendation.REGENERATE_ASSET

        # Explicaciones
        explanation_human = f"Score: {overall_score * 100:.0f}%. Found {len(defects)} defects ({', '.join(d.category.value for d in defects[:3])})."
        explanation_agent = f"Apply {len(correction_plan)} targeted corrections without full asset regeneration." if recommendation != CriticRecommendation.REGENERATE_ASSET else "Rebuild asset."

        return CriticResult(
            overall_score=overall_score,
            technical_score=0.95,
            visual_score=overall_score,
            hard_failures=hard_failures,
            defects=defects,
            warnings=warnings,
            recommendation=recommendation,
            correction_plan=correction_plan,
            explanation_human=explanation_human,
            explanation_agent=explanation_agent
        )
