import uuid
from typing import Dict, Any, List, Optional
from ..core.evaluation_schema import (
    EvaluationReport, EvaluationFailure, EvaluationDimension, EvaluationSeverity,
    ExpectedVisualProfile, RepairScope
)
from ..core.evaluation_profiles import EvaluationProfile

class MultiDimensionEvaluator:
    @staticmethod
    def evaluate(
        target_id: str,
        actual_data: Dict[str, Any],
        expected_profile: ExpectedVisualProfile,
        profile: EvaluationProfile
    ) -> EvaluationReport:
        dim_scores: Dict[str, float] = {}
        failures: List[EvaluationFailure] = []

        # 1. SEMANTIC EVALUATION
        actual_comps = actual_data.get("components", [])
        missing_comps = [c for c in expected_profile.expected_components if c not in actual_comps]
        if missing_comps:
            for mc in missing_comps:
                failures.append(EvaluationFailure(
                    code="MISSING_REQUIRED_ASSET",
                    severity=EvaluationSeverity.CRITICAL,
                    entity_id=target_id,
                    dimension=EvaluationDimension.SEMANTIC,
                    expected=mc,
                    actual="MISSING",
                    suggested_scope=RepairScope.ASSET,
                    suggested_action=f"Create missing required asset '{mc}'"
                ))
            dim_scores["SEMANTIC"] = 0.40
        else:
            dim_scores["SEMANTIC"] = 1.00

        # 2. SCALE EVALUATION
        actual_dims = actual_data.get("dimensions", {})
        scale_score = 1.0
        for dim_name, exp_val in expected_profile.target_dimensions.items():
            act_val = actual_dims.get(dim_name)
            if act_val is not None:
                diff = abs(act_val - exp_val)
                if diff > 0.05: # tolerancia > 5cm
                    failures.append(EvaluationFailure(
                        code="SCALE_MISMATCH",
                        severity=EvaluationSeverity.ERROR,
                        entity_id=target_id,
                        dimension=EvaluationDimension.SCALE,
                        expected=exp_val,
                        actual=act_val,
                        parameter_name=dim_name,
                        suggested_scope=RepairScope.PARAMETER,
                        suggested_action=f"Set parameter '{dim_name}' from {act_val} to {exp_val}"
                    ))
                    scale_score = max(0.20, scale_score - 0.40)
        dim_scores["SCALE"] = scale_score

        # 3. PROPORTION EVALUATION
        act_roof_h = actual_data.get("component_measurements", {}).get("roof_height")
        if act_roof_h is not None and act_roof_h > 1.0: # si el tejado mide 1.35m vs 0.80m
            failures.append(EvaluationFailure(
                code="PROPORTION_MISMATCH",
                severity=EvaluationSeverity.ERROR,
                entity_id=target_id,
                dimension=EvaluationDimension.PROPORTION,
                expected=0.80,
                actual=act_roof_h,
                component_id="roof",
                parameter_name="roof_height",
                suggested_scope=RepairScope.COMPONENT,
                suggested_action="Reduce roof_height from 1.35m to 0.80m"
            ))
            dim_scores["PROPORTION"] = 0.50
        else:
            dim_scores["PROPORTION"] = 1.00

        # 4. SPATIAL EVALUATION
        actual_spatial = actual_data.get("spatial_relations", {})
        spatial_score = 1.0
        for entity_k, exp_rel in expected_profile.expected_spatial_relations.items():
            act_rel = actual_spatial.get(entity_k)
            if act_rel and act_rel != exp_rel:
                failures.append(EvaluationFailure(
                    code="SPATIAL_RELATIONSHIP_FAILURE",
                    severity=EvaluationSeverity.ERROR,
                    entity_id=entity_k,
                    dimension=EvaluationDimension.SPATIAL,
                    expected=exp_rel,
                    actual=act_rel,
                    suggested_scope=RepairScope.ASSET,
                    suggested_action=f"Move '{entity_k}' from {act_rel} to {exp_rel}"
                ))
                spatial_score = 0.40
        dim_scores["SPATIAL"] = spatial_score

        # 5. TECHNICAL EVALUATION
        act_poly = actual_data.get("polycount", 1000)
        if act_poly > expected_profile.target_polycount:
            failures.append(EvaluationFailure(
                code="POLYCOUNT_EXCEEDED",
                severity=EvaluationSeverity.WARNING,
                entity_id=target_id,
                dimension=EvaluationDimension.TECHNICAL,
                expected=expected_profile.target_polycount,
                actual=act_poly,
                suggested_scope=RepairScope.ASSET,
                suggested_action="Reduce geometry detail"
            ))
            dim_scores["TECHNICAL"] = 0.60
        else:
            dim_scores["TECHNICAL"] = 1.00

        # SHAPE & STYLE DEFAULTS
        dim_scores["SHAPE"] = actual_data.get("shape_score", 1.00)
        dim_scores["STYLE"] = 1.00
        dim_scores["MATERIAL"] = 1.00

        # Ponderación Global
        total_w = sum(profile.weights.get(k, 0.10) for k in dim_scores)
        overall = sum(dim_scores[k] * profile.weights.get(k, 0.10) for k in dim_scores) / max(0.01, total_w)

        return EvaluationReport(
            evaluation_id=f"eval_{uuid.uuid4().hex[:6]}",
            target_id=target_id,
            overall_score=round(overall, 4),
            dimension_scores=dim_scores,
            failures=failures
        )
