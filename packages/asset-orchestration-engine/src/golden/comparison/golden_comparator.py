from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.golden_models import GoldenAsset
from ..core.golden_types import RegressionLevel
from .regression_policy import RegressionPolicy
from ...evaluation import EvaluationBenchmark, DefectSeverity

@dataclass
class GoldenComparisonResult:
    overall_status: RegressionLevel
    overall_delta: float
    geometry_delta: float = 0.0
    material_delta: float = 0.0
    visual_delta: float = 0.0
    uv_delta: float = 0.0
    lod_delta: float = 0.0
    collision_delta: float = 0.0
    unreal_readiness_delta: float = 0.0
    regression_detected: bool = False
    critical_regression: bool = False
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "overall_delta": round(self.overall_delta, 4),
            "geometry_delta": round(self.geometry_delta, 4),
            "material_delta": round(self.material_delta, 4),
            "visual_delta": round(self.visual_delta, 4),
            "uv_delta": round(self.uv_delta, 4),
            "lod_delta": round(self.lod_delta, 4),
            "collision_delta": round(self.collision_delta, 4),
            "unreal_readiness_delta": round(self.unreal_readiness_delta, 4),
            "regression_detected": self.regression_detected,
            "critical_regression": self.critical_regression,
            "evidence": self.evidence
        }

class GoldenComparator:
    """Compares candidate evaluation benchmarks against official Golden Assets."""
    
    @classmethod
    def compare(
        cls,
        candidate_bench: EvaluationBenchmark,
        golden_asset: GoldenAsset,
        policy: Optional[RegressionPolicy] = None
    ) -> GoldenComparisonResult:
        pol = policy or RegressionPolicy()
        c_score = candidate_bench.weighted_score
        g_score = golden_asset.baseline_score

        overall_delta = round(c_score - g_score, 4)
        cand_dims = {k.value: v.score for k, v in candidate_bench.dimension_scores.items()}

        geo_d = round(cand_dims.get("GEOMETRY", 1.0) - 1.0, 4)
        mat_d = round(cand_dims.get("MATERIAL", 1.0) - 1.0, 4)
        vis_d = round(cand_dims.get("VISUAL_MATCH", 0.9) - 0.9, 4)
        uv_d = round(cand_dims.get("UV", 1.0) - 1.0, 4)
        lod_d = round(cand_dims.get("LOD", 1.0) - 1.0, 4)
        col_d = round(cand_dims.get("COLLISION", 1.0) - 1.0, 4)
        ue_d = round(cand_dims.get("ENGINE_READINESS", 1.0) - 1.0, 4)

        dim_deltas = {
            "GEOMETRY": geo_d,
            "MATERIAL": mat_d,
            "VISUAL_MATCH": vis_d,
            "UV": uv_d,
            "LOD": lod_d,
            "COLLISION": col_d,
            "ENGINE_READINESS": ue_d
        }

        has_crit = any(d.severity == DefectSeverity.CRITICAL or d.blocking for d in candidate_bench.defects)
        status = pol.evaluate_regression(c_score, g_score, dim_deltas, has_critical_defect=has_crit)

        is_regr = status in (RegressionLevel.REGRESSION, RegressionLevel.CRITICAL_REGRESSION)
        is_crit = (status == RegressionLevel.CRITICAL_REGRESSION)

        return GoldenComparisonResult(
            overall_status=status,
            overall_delta=overall_delta,
            geometry_delta=geo_d,
            material_delta=mat_d,
            visual_delta=vis_d,
            uv_delta=uv_d,
            lod_delta=lod_d,
            collision_delta=col_d,
            unreal_readiness_delta=ue_d,
            regression_detected=is_regr,
            critical_regression=is_crit,
            evidence={
                "golden_id": golden_asset.golden_id,
                "candidate_id": candidate_bench.candidate_id,
                "golden_score": round(g_score, 4),
                "candidate_score": round(c_score, 4)
            }
        )
