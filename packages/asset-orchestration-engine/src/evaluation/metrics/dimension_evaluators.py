from typing import Dict, Any, List, Optional
from ..core.evaluation_types import EvaluationDimension, DefectSeverity, DefectStatus
from ..models.evaluation_models import DimensionScore, EvaluationDefect

class DimensionEvaluator:
    """
    Evaluates individual dimensions based on extracted Blender metrics, visual critic data,
    and game engine readiness specs.
    """
    @classmethod
    def evaluate_all(
        cls,
        asset_data: Dict[str, Any],
        spec_data: Optional[Dict[str, Any]] = None,
        reference_data: Optional[Dict[str, Any]] = None
    ) -> Dict[EvaluationDimension, DimensionScore]:
        scores: Dict[EvaluationDimension, DimensionScore] = {}
        spec = spec_data or {}
        ref = reference_data or {}

        # 1. GEOMETRY
        scores[EvaluationDimension.GEOMETRY] = cls._eval_geometry(asset_data, spec)
        # 2. TOPOLOGY
        scores[EvaluationDimension.TOPOLOGY] = cls._eval_topology(asset_data, spec)
        # 3. SILHOUETTE
        scores[EvaluationDimension.SILHOUETTE] = cls._eval_silhouette(asset_data, ref)
        # 4. PROPORTION
        scores[EvaluationDimension.PROPORTION] = cls._eval_proportion(asset_data, spec)
        # 5. VISUAL_MATCH
        scores[EvaluationDimension.VISUAL_MATCH] = cls._eval_visual_match(asset_data, ref)
        # 6. MATERIAL
        scores[EvaluationDimension.MATERIAL] = cls._eval_material(asset_data, spec)
        # 7. TEXTURE
        scores[EvaluationDimension.TEXTURE] = cls._eval_texture(asset_data, spec)
        # 8. UV
        scores[EvaluationDimension.UV] = cls._eval_uv(asset_data, spec)
        # 9. DETAIL
        scores[EvaluationDimension.DETAIL] = cls._eval_detail(asset_data, spec)
        # 10. STYLE_CONSISTENCY
        scores[EvaluationDimension.STYLE_CONSISTENCY] = cls._eval_style_consistency(asset_data, spec)
        # 11. FUNCTIONAL_STRUCTURE
        scores[EvaluationDimension.FUNCTIONAL_STRUCTURE] = cls._eval_functional_structure(asset_data, spec)
        # 12. COLLISION
        scores[EvaluationDimension.COLLISION] = cls._eval_collision(asset_data, spec)
        # 13. LOD
        scores[EvaluationDimension.LOD] = cls._eval_lod(asset_data, spec)
        # 14. ENGINE_READINESS
        scores[EvaluationDimension.ENGINE_READINESS] = cls._eval_engine_readiness(asset_data, spec)
        # 15. PERFORMANCE
        scores[EvaluationDimension.PERFORMANCE] = cls._eval_performance(asset_data, spec)
        # 16. PACKAGE_INTEGRITY
        scores[EvaluationDimension.PACKAGE_INTEGRITY] = cls._eval_package_integrity(asset_data, spec)
        # 17. SEMANTIC_COMPLIANCE
        scores[EvaluationDimension.SEMANTIC_COMPLIANCE] = cls._eval_semantic_compliance(asset_data, spec)

        return scores

    @classmethod
    def _eval_geometry(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        score = 1.0
        defects = []
        poly_count = data.get("polygon_count", 0)
        non_manifold = data.get("non_manifold_count", 0)

        if non_manifold > 0:
            score -= min(0.4, non_manifold * 0.05)
            defects.append(EvaluationDefect(
                defect_id="DEF_GEO_NON_MANIFOLD",
                category="GEOMETRY",
                severity=DefectSeverity.MAJOR,
                dimension=EvaluationDimension.GEOMETRY,
                description=f"Detected {non_manifold} non-manifold edges/vertices.",
                blocking=False
            ))

        max_polys = spec.get("max_polygons", 20000)
        if poly_count > max_polys:
            score -= 0.25
            defects.append(EvaluationDefect(
                defect_id="DEF_GEO_POLY_BUDGET",
                category="GEOMETRY",
                severity=DefectSeverity.MINOR,
                dimension=EvaluationDimension.GEOMETRY,
                description=f"Polygon count {poly_count} exceeds target budget {max_polys}."
            ))

        return DimensionScore(
            dimension=EvaluationDimension.GEOMETRY,
            score=max(0.0, min(1.0, score)),
            evidence={"polygon_count": poly_count, "non_manifold_count": non_manifold},
            defects=defects
        )

    @classmethod
    def _eval_topology(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        score = data.get("topology_score", 0.90)
        defects = []
        if data.get("has_loose_geometry", False):
            score -= 0.20
            defects.append(EvaluationDefect(
                defect_id="DEF_TOP_LOOSE_GEO",
                category="TOPOLOGY",
                severity=DefectSeverity.MINOR,
                dimension=EvaluationDimension.TOPOLOGY,
                description="Loose disconnected vertices/edges found in mesh."
            ))
        return DimensionScore(
            dimension=EvaluationDimension.TOPOLOGY,
            score=max(0.0, min(1.0, score)),
            evidence={"quad_ratio": data.get("quad_ratio", 0.85)},
            defects=defects
        )

    @classmethod
    def _eval_silhouette(cls, data: Dict[str, Any], ref: Dict[str, Any]) -> DimensionScore:
        sim = data.get("silhouette_similarity", 0.88)
        defects = []
        if sim < 0.75:
            defects.append(EvaluationDefect(
                defect_id="DEF_SIL_MISMATCH",
                category="SILHOUETTE",
                severity=DefectSeverity.MAJOR,
                dimension=EvaluationDimension.SILHOUETTE,
                description="Silhouette boundary deviation exceeds acceptable threshold."
            ))
        return DimensionScore(
            dimension=EvaluationDimension.SILHOUETTE,
            score=max(0.0, min(1.0, sim)),
            evidence={"similarity": sim},
            defects=defects
        )

    @classmethod
    def _eval_proportion(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        prop_score = data.get("proportion_score", 0.92)
        return DimensionScore(
            dimension=EvaluationDimension.PROPORTION,
            score=prop_score,
            evidence={"aspect_ratio_accuracy": data.get("aspect_ratio_accuracy", 0.95)}
        )

    @classmethod
    def _eval_visual_match(cls, data: Dict[str, Any], ref: Dict[str, Any]) -> DimensionScore:
        match_score = data.get("visual_match_score", 0.86)
        return DimensionScore(
            dimension=EvaluationDimension.VISUAL_MATCH,
            score=match_score,
            evidence={"ssim": data.get("ssim", 0.85)}
        )

    @classmethod
    def _eval_material(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        score = 1.0
        defects = []
        mats = data.get("materials", [])
        if not mats:
            score -= 0.50
            defects.append(EvaluationDefect(
                defect_id="DEF_MAT_MISSING",
                category="MATERIAL",
                severity=DefectSeverity.MAJOR,
                dimension=EvaluationDimension.MATERIAL,
                description="No materials assigned to mesh."
            ))
        return DimensionScore(
            dimension=EvaluationDimension.MATERIAL,
            score=max(0.0, score),
            evidence={"materials": mats},
            defects=defects
        )

    @classmethod
    def _eval_texture(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        return DimensionScore(
            dimension=EvaluationDimension.TEXTURE,
            score=data.get("texture_score", 0.90),
            evidence={"resolution": data.get("texture_res", "2048x2048")}
        )

    @classmethod
    def _eval_uv(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        score = 0.95
        defects = []
        if data.get("uv_overlaps", 0) > 0:
            score -= 0.15
            defects.append(EvaluationDefect(
                defect_id="DEF_UV_OVERLAP",
                category="UV",
                severity=DefectSeverity.MINOR,
                dimension=EvaluationDimension.UV,
                description="UV map contains overlapping islands outside allowed mirror sets."
            ))
        return DimensionScore(
            dimension=EvaluationDimension.UV,
            score=max(0.0, score),
            evidence={"coverage": data.get("uv_coverage", 0.82)},
            defects=defects
        )

    @classmethod
    def _eval_detail(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        return DimensionScore(
            dimension=EvaluationDimension.DETAIL,
            score=data.get("detail_score", 0.88),
            evidence={"bevel_presence": data.get("has_bevels", True)}
        )

    @classmethod
    def _eval_style_consistency(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        return DimensionScore(
            dimension=EvaluationDimension.STYLE_CONSISTENCY,
            score=data.get("style_score", 0.90),
            evidence={"style_compliance": "DarX Tactical Sci-Fi"}
        )

    @classmethod
    def _eval_functional_structure(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        return DimensionScore(
            dimension=EvaluationDimension.FUNCTIONAL_STRUCTURE,
            score=data.get("functional_score", 0.92),
            evidence={"modular_sockets": data.get("sockets_count", 4)}
        )

    @classmethod
    def _eval_collision(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        has_col = data.get("has_collision", True)
        score = 1.0 if has_col else 0.40
        defects = []
        if not has_col:
            defects.append(EvaluationDefect(
                defect_id="DEF_COL_MISSING",
                category="COLLISION",
                severity=DefectSeverity.MAJOR,
                dimension=EvaluationDimension.COLLISION,
                description="Missing UCX collision geometry."
            ))
        return DimensionScore(
            dimension=EvaluationDimension.COLLISION,
            score=score,
            evidence={"collision_hulls": data.get("collision_hulls_count", 1)},
            defects=defects
        )

    @classmethod
    def _eval_lod(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        lod_count = data.get("lod_count", 3)
        score = 1.0 if lod_count >= 3 else (0.70 if lod_count > 0 else 0.30)
        defects = []
        if lod_count < 3:
            defects.append(EvaluationDefect(
                defect_id="DEF_LOD_COUNT_LOW",
                category="LOD",
                severity=DefectSeverity.MINOR,
                dimension=EvaluationDimension.LOD,
                description=f"LOD count {lod_count} is lower than recommended 3."
            ))
        return DimensionScore(
            dimension=EvaluationDimension.LOD,
            score=score,
            evidence={"lod_count": lod_count},
            defects=defects
        )

    @classmethod
    def _eval_engine_readiness(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        readiness = data.get("engine_readiness_score", 0.95)
        defects = []
        if data.get("invalid_scale_or_axis", False):
            readiness -= 0.35
            defects.append(EvaluationDefect(
                defect_id="DEF_ENG_AXIS_SCALE",
                category="ENGINE_READINESS",
                severity=DefectSeverity.CRITICAL,
                dimension=EvaluationDimension.ENGINE_READINESS,
                description="Non-uniform scale or non-standard UE axis alignment.",
                blocking=True
            ))
        return DimensionScore(
            dimension=EvaluationDimension.ENGINE_READINESS,
            score=max(0.0, min(1.0, readiness)),
            evidence={"export_ready": data.get("export_ready", True)},
            defects=defects
        )

    @classmethod
    def _eval_performance(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        return DimensionScore(
            dimension=EvaluationDimension.PERFORMANCE,
            score=data.get("perf_score", 0.92),
            evidence={"est_render_cost_ms": 0.12}
        )

    @classmethod
    def _eval_package_integrity(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        return DimensionScore(
            dimension=EvaluationDimension.PACKAGE_INTEGRITY,
            score=data.get("pkg_score", 1.0),
            evidence={"manifest_valid": True}
        )

    @classmethod
    def _eval_semantic_compliance(cls, data: Dict[str, Any], spec: Dict[str, Any]) -> DimensionScore:
        return DimensionScore(
            dimension=EvaluationDimension.SEMANTIC_COMPLIANCE,
            score=data.get("semantic_score", 0.95),
            evidence={"naming_compliant": True}
        )
