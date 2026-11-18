from typing import Dict, Any, List
from ..core.reference_schema import (
    ReferenceProfile, ErrorMap, GeometricDiscrepancy, ProportionFeature
)
from ..analysis.feature_extractor import FeatureExtractor

class GeometricMatcher:
    @staticmethod
    def compare_model_against_reference(
        target_asset_id: str,
        model_data: Dict[str, Any],
        reference: ReferenceProfile
    ) -> ErrorMap:
        actual_features = FeatureExtractor.extract_model_features(model_data)
        discrepancies: List[GeometricDiscrepancy] = []
        recommended_patches: Dict[str, float] = {}

        # 1. Comprobar componentes faltantes / inesperados
        act_comps = set(actual_features["components"])
        exp_comps = set(reference.detected_components)
        missing = sorted(list(exp_comps - act_comps))
        unexpected = sorted(list(act_comps - exp_comps))

        # 2. Comprobar discrepancias de proporciones
        act_props = actual_features["proportions"]
        score_penalties = 0.0

        # Proporción Tejado vs Paredes
        exp_roof_ratio = reference.proportions.get("roof_to_wall_ratio")
        if exp_roof_ratio:
            act_roof_ratio = act_props["roof_to_wall_ratio"].value
            diff = exp_roof_ratio.value - act_roof_ratio
            if abs(diff) > exp_roof_ratio.tolerance:
                pct = round((diff / exp_roof_ratio.value) * 100.0, 1)
                curr_roof_h = model_data.get("parameters", {}).get("roof_height", 1.75)
                new_roof_h = round(curr_roof_h * (1.0 + pct / 100.0), 3)
                discrepancies.append(GeometricDiscrepancy(
                    component="roof",
                    parameter_hint="roof_height",
                    expected_value=exp_roof_ratio.value,
                    actual_value=act_roof_ratio,
                    delta_percent=pct,
                    severity="ERROR",
                    description="El techo está demasiado bajo respecto a la referencia."
                ))
                recommended_patches["roof_height"] = new_roof_h
                score_penalties += 0.15

        # Escala de Ventanas
        exp_win_scale = reference.proportions.get("window_scale")
        if exp_win_scale:
            act_win_scale = act_props["window_scale"].value
            diff_win = exp_win_scale.value - act_win_scale
            if abs(diff_win) > exp_win_scale.tolerance:
                pct_win = round((diff_win / exp_win_scale.value) * 100.0, 1)
                discrepancies.append(GeometricDiscrepancy(
                    component="windows",
                    parameter_hint="window_scale",
                    expected_value=exp_win_scale.value,
                    actual_value=act_win_scale,
                    delta_percent=pct_win,
                    severity="ERROR",
                    description="Las ventanas están demasiado pequeñas respecto a la referencia."
                ))
                recommended_patches["window_scale"] = exp_win_scale.value
                score_penalties += 0.12

        # Puntuaciones
        sil_sim = max(0.40, round(1.0 - (len(discrepancies) * 0.15) - (0.25 if missing else 0.0), 3))
        overall_score = max(0.40, round(1.0 - score_penalties - (0.30 if missing else 0.0), 3))

        return ErrorMap(
            reference_id=reference.reference_id,
            target_asset_id=target_asset_id,
            silhouette_similarity=sil_sim,
            overall_geometric_score=overall_score,
            discrepancies=discrepancies,
            missing_components=missing,
            unexpected_components=unexpected,
            recommended_patches=recommended_patches
        )
