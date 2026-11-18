import time
from typing import Dict, Any, List, Optional
from ..core.reference_types import (
    ReferenceRole, SpecificationPriority
)
from ..core.reference_schema import (
    ReferenceItem, VisualSpecification, StructuralSpecification,
    ProportionConstraint, FeatureParameterAttribution
)
from ..analyzers.visual_feature_extractor import VisualFeatureExtractor
from ..analyzers.material_style_analyzer import MaterialStyleAnalyzer
from ..analyzers.uncertainty_evaluator import UncertaintyEvaluator

class SpecificationCompiler:
    @staticmethod
    def compile_visual_specification(
        references: List[ReferenceItem],
        archetype_id: str = "MEDIEVAL_HOUSE",
        user_prompt: str = ""
    ) -> VisualSpecification:
        # Detectar conflictos entre referencias primarias
        primary_refs = [r for r in references if r.role == ReferenceRole.PRIMARY]
        if len(primary_refs) > 1:
            r1_aspect = primary_refs[0].metadata.get("aspect_ratio", 1.52)
            r2_aspect = primary_refs[1].metadata.get("aspect_ratio", 1.52)
            if abs(r1_aspect - r2_aspect) > 0.30:
                raise ValueError(f"REFERENCE_CONFLICT: Primary references contradict on aspect ratio ({r1_aspect} vs {r2_aspect}).")

        primary = primary_refs[0] if primary_refs else references[0]
        
        # Ejecutar análisis
        features = VisualFeatureExtractor.extract_features_from_reference(primary, user_prompt)
        mat_style = MaterialStyleAnalyzer.analyze_materials_and_style(primary)
        uncertainties = UncertaintyEvaluator.evaluate_uncertainties(
            has_multi_view=len(references) > 1,
            has_explicit_scale="meters" in user_prompt or "width" in user_prompt
        )

        spec_id = f"VSPEC_{int(time.time()*1000)}"

        return VisualSpecification(
            spec_id=spec_id,
            archetype_id=archetype_id,
            aspect_ratio=features["aspect_ratio"],
            roof_ratio=features["roof_ratio"],
            detected_components=features["components"],
            landmarks=features["landmarks"],
            materials=mat_style["materials"],
            dominant_colors=mat_style["dominant_colors"],
            detail_treatments=mat_style["detail_treatments"],
            uncertainties=uncertainties,
            overall_confidence=0.94
        )

    @staticmethod
    def translate_to_structural_specification(
        vspec: VisualSpecification,
        user_overrides: Optional[Dict[str, Any]] = None
    ) -> StructuralSpecification:
        target_params: Dict[str, Any] = {
            "width": 8.0,
            "depth": 6.0,
            "wall_height": 3.0,
            "roof_height": round(3.0 * (vspec.roof_ratio / (1.0 - vspec.roof_ratio)), 2), # ~ 1.35m - 1.45m
            "roof_pitch": 35.0,
            "window_count": vspec.detected_components.get("windows", None).count if "windows" in vspec.detected_components else 4,
            "door_count": 1,
            "wall_material": vspec.materials.get("walls", "STONE"),
            "roof_material": vspec.materials.get("roof", "WOOD")
        }

        # Aplicar Prioridad de Sobrescritura de Usuario (USER_EXPLICIT > REFERENCE_OBSERVED)
        if user_overrides:
            target_params.update(user_overrides)

        constraints = [
            ProportionConstraint("ROOF_BODY_RATIO", target_value=vspec.roof_ratio, tolerance=0.03, confidence=0.95),
            ProportionConstraint("ASPECT_RATIO_H_W", target_value=vspec.aspect_ratio, tolerance=0.05, confidence=0.93)
        ]

        gameplay_constraints = {
            "min_door_width": 1.0,
            "min_door_height": 2.1,
            "collision_required": True
        }

        feature_param_map = {
            "roof_silhouette": FeatureParameterAttribution("roof_silhouette", ["roof_height", "roof_width", "roof_pitch"], "HIGH", 0.95),
            "facade_proportions": FeatureParameterAttribution("facade_proportions", ["width", "wall_height"], "HIGH", 0.94),
            "openings_layout": FeatureParameterAttribution("openings_layout", ["window_count", "door_count"], "MEDIUM", 0.90)
        }

        struct_id = f"SSPEC_{vspec.spec_id.replace('VSPEC_', '')}"

        return StructuralSpecification(
            spec_id=struct_id,
            visual_spec_id=vspec.spec_id,
            archetype_id=vspec.archetype_id,
            target_parameters=target_params,
            constraints=constraints,
            gameplay_constraints=gameplay_constraints,
            feature_parameter_map=feature_param_map
        )
