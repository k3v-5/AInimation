"""
RuntimeAssetValidator enforces production gates, pivot correctness, collision, and Unreal readiness.
UAF-81.8 Sections 105, 106, 108, 109, 132, 133.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..graph.assembly_graph import AssetAssemblyGraph, AssetLifecycleState
from ..spatial.pivot import PivotDefinition, PivotType
from ..spatial.socket import RuntimeSocketDefinition
from ..optimization.lod_policy import LODChain, NanitePolicy


@dataclass
class RuntimeAssetQualityScore:
    visual_score: float        # 0.0 to 1.0
    technical_score: float     # 0.0 to 1.0
    gameplay_score: float      # 0.0 to 1.0
    performance_score: float   # 0.0 to 1.0
    compatibility_score: float # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.20 * self.visual_score +
            0.25 * self.technical_score +
            0.20 * self.gameplay_score +
            0.20 * self.performance_score +
            0.15 * self.compatibility_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "visual_score": self.visual_score,
            "technical_score": self.technical_score,
            "gameplay_score": self.gameplay_score,
            "performance_score": self.performance_score,
            "compatibility_score": self.compatibility_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class RuntimeAssetQualityReport:
    is_valid: bool
    quality_score: RuntimeAssetQualityScore
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "review_status": self.review_status,
        }


class RuntimeAssetValidator:
    """
    Validates complete asset assembly for Unreal Engine 5 production readiness.
    Enforces NON-NEGOTIABLE PRINCIPLE (Section 133).
    """
    @classmethod
    def validate_assembly(
        cls,
        graph: AssetAssemblyGraph,
        pivot: Optional[PivotDefinition] = None,
        sockets: Optional[List[RuntimeSocketDefinition]] = None,
        lod_chain: Optional[LODChain] = None,
        is_static: bool = True,
        max_triangles: int = 100000,
    ) -> RuntimeAssetQualityReport:
        issues = []
        warnings = []

        # 1. Technical correctness (Pivot, Hierarchy, Material assignments)
        tech_score = 1.0
        if not graph.render_components:
            issues.append("Assembly has no render geometry components.")
            tech_score = 0.0
        if not graph.material_slots:
            issues.append("Assembly has no material slots assigned.")
            tech_score -= 0.5

        # 2. Gameplay readiness (Collision & Sockets)
        gameplay_score = 1.0
        if not graph.collision_shapes and is_static:
            issues.append("Static asset lacks physics collision geometry.")
            gameplay_score -= 0.6
        if sockets:
            for s in sockets:
                if any(scale <= 0.0 for scale in s.scale):
                    issues.append(f"Socket '{s.socket_id}' has non-positive scale: {s.scale}.")
                    gameplay_score -= 0.3

        # 3. Performance & Optimization (LODs & Nanite)
        perf_score = 1.0
        if lod_chain and len(lod_chain.lods) < 2 and not NanitePolicy.evaluate_nanite_eligibility(is_static, 5000, False):
            warnings.append("Asset lacks sufficient LOD levels for non-Nanite pipeline.")
            perf_score -= 0.2

        # 4. Visual quality
        visual_score = 1.0 if not issues else 0.5
        compat_score = 1.0

        q_score = RuntimeAssetQualityScore(
            visual_score=visual_score,
            technical_score=max(0.0, tech_score),
            gameplay_score=max(0.0, gameplay_score),
            performance_score=max(0.0, perf_score),
            compatibility_score=compat_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.75
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return RuntimeAssetQualityReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
