import time
from typing import Dict, Any, List, Optional
from ..core.reference_types import (
    ReferenceModality, CameraPerspective, ExtractedMaterialType,
    StyleArchetype, ConfidenceTier, VisualFeatureImportance
)
from ..core.reference_schema import (
    ImageReferenceInput, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ColorPalette, CameraEstimation,
    VisualRequirementItem, DecomposedReferenceReport
)
from ..analyzers.silhouette_extractor import SilhouetteExtractor
from ..analyzers.proportion_estimator import ProportionEstimator
from ..analyzers.part_decomposer import PartDecomposer
from ..analyzers.material_color_analyzer import MaterialColorAnalyzer
from ..analyzers.camera_view_estimator import CameraViewEstimator

class ReferenceDecompositionEngine:
    @classmethod
    def decompose(
        cls,
        references: List[ImageReferenceInput],
        asset_class_hint: str = "PROP.BARREL",
        target_style: StyleArchetype = StyleArchetype.STYLIZED
    ) -> DecomposedReferenceReport:
        if not references:
            raise ValueError("INVALID_REFERENCE: At least one ImageReferenceInput is required.")

        ref_ids = [r.reference_id for r in references]
        primary_ref = next((r for r in references if r.role == "PRIMARY"), references[0])
        meta = primary_ref.metadata or {}

        warnings: List[str] = []

        # 1. Detección de Contradicciones Multi-Referencia
        styles_found = {r.metadata.get("style", "STYLIZED") for r in references if r.metadata}
        if len(styles_found) > 1:
            warnings.append(f"STYLE_CONFLICT: Contradictory styles detected across references: {styles_found}. Prioritizing PRIMARY reference.")

        # 2. Extracciones de Componentes
        sil = SilhouetteExtractor.extract_silhouette(meta)
        prop = ProportionEstimator.estimate_proportions(meta)
        parts = PartDecomposer.decompose_parts(asset_class_hint, meta)
        mat_pal, col_pal = MaterialColorAnalyzer.extract_materials_and_colors(meta)
        cam = CameraViewEstimator.estimate_camera(meta)

        # 3. Compilación de VisualRequirementItems estructurados
        reqs = [
            VisualRequirementItem("REQ_SIL_ASPECT", "SILHOUETTE", "Height-to-width aspect ratio matching reference", sil.aspect_ratio, VisualFeatureImportance.CRITICAL, sil.silhouette_confidence),
            VisualRequirementItem("REQ_CURVATURE", "PROPORTION", "Barrel bulging profile curvature", prop.estimated_curvature, VisualFeatureImportance.HIGH, 0.92),
            VisualRequirementItem("REQ_BASE_MATERIAL", "MATERIAL", "Base structure material", mat_pal.base_material.value, VisualFeatureImportance.HIGH, 0.95),
            VisualRequirementItem("REQ_DOMINANT_COLOR", "COLOR", "Primary surface color distribution", col_pal.dominant_colors[0], VisualFeatureImportance.MEDIUM, 0.90)
        ]

        for p in parts:
            reqs.append(VisualRequirementItem(
                requirement_id=f"REQ_PART_{p.part_id.upper()}",
                category="COMPONENT",
                description=f"Identified functional component: {p.semantic_type}",
                target_value=p.semantic_type,
                importance=VisualFeatureImportance.HIGH if p.is_primary else VisualFeatureImportance.MEDIUM,
                confidence=p.confidence
            ))

        # 4. Cálculo de Confianza Global
        confidences = [sil.silhouette_confidence, prop.tolerance, mat_pal.surface_roughness] + [p.confidence for p in parts]
        overall_conf = round(sum(p.confidence for p in parts) / max(len(parts), 1), 2)

        return DecomposedReferenceReport(
            report_id=f"REP_REF_{int(time.time()*1000)}",
            reference_ids=ref_ids,
            asset_class_hint=asset_class_hint,
            style_archetype=target_style,
            silhouette=sil,
            proportions=prop,
            parts=parts,
            materials=mat_pal,
            colors=col_pal,
            camera=cam,
            visual_requirements=reqs,
            overall_confidence=overall_conf,
            warnings=warnings
        )
