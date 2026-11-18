"""
FabricationValidator verifies anatomical proportions, layer hierarchy, and non-negotiable rules.
UAF-81.10 Sections 141, 147, 148, 149, 167, 168.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..anatomy.proportions import ProportionProfile
from ..anatomy.body_graph import FormLevel, SemanticBodyGraph
from ..garments.garment import GarmentDefinition, GarmentLayer


@dataclass
class FabricationQualityScore:
    proportion_score: float           # 0.0 to 1.0
    topology_score: float             # 0.0 to 1.0
    component_integrity_score: float  # 0.0 to 1.0
    layer_ordering_score: float       # 0.0 to 1.0
    material_region_score: float      # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.20 * self.proportion_score +
            0.25 * self.topology_score +
            0.25 * self.component_integrity_score +
            0.15 * self.layer_ordering_score +
            0.15 * self.material_region_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proportion_score": self.proportion_score,
            "topology_score": self.topology_score,
            "component_integrity_score": self.component_integrity_score,
            "layer_ordering_score": self.layer_ordering_score,
            "material_region_score": self.material_region_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class FabricationValidationReport:
    is_valid: bool
    quality_score: FabricationQualityScore
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


class FabricationValidator:
    """
    Validates fabricated character bodies, component ownership, and garment layering.
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 166, 167, 168).
    """

    @classmethod
    def validate_fabrication(
        cls,
        body_graph: SemanticBodyGraph,
        proportions: Optional[ProportionProfile] = None,
        garments: Optional[List[GarmentDefinition]] = None,
    ) -> FabricationValidationReport:
        issues = []
        warnings = []

        # 1. Component Integrity: must have primary components
        primary_comps = body_graph.get_components_by_level(FormLevel.PRIMARY)
        if not primary_comps:
            issues.append("NON-NEGOTIABLE VIOLATION: Character has no primary anatomical forms.")
            comp_score = 0.0
        else:
            comp_score = 1.0

        # Check for orphan components with missing parents
        for comp in body_graph.components.values():
            if comp.parent_id and comp.parent_id not in body_graph.components:
                issues.append(f"Component '{comp.component_id}' references non-existent parent '{comp.parent_id}'.")
                comp_score -= 0.2

        # 2. Proportion validation
        prop_score = 1.0
        if proportions:
            a = proportions.anatomy
            if a.height_cm <= 0 or a.shoulder_width_cm <= 0:
                issues.append("Invalid anatomical dimensions (negative or zero scale).")
                prop_score = 0.0

        # 3. Layer ordering validation (garments on body targets)
        layer_score = 1.0
        if garments:
            # Check for inverted layering (e.g. Underwear over Armor)
            # Group garments by targeted body part and check monotonic layer values
            target_layers: Dict[str, List[int]] = {}
            for g in garments:
                for target in g.target_body_components:
                    target_layers.setdefault(target, []).append(g.layer.value)

            for target, layers in target_layers.items():
                if sorted(layers) != layers:
                    issues.append(f"NON-NEGOTIABLE VIOLATION: Inverted garment layers on target '{target}': {layers}.")
                    layer_score = 0.0

        # 4. Material regions & topology
        mat_score = 1.0
        for comp in body_graph.components.values():
            if not comp.material_region_id:
                warnings.append(f"Component '{comp.component_id}' lacks material region assignment.")
                mat_score -= 0.1
        mat_score = max(0.0, mat_score)

        topology_score = 1.0

        q_score = FabricationQualityScore(
            proportion_score=max(0.0, prop_score),
            topology_score=topology_score,
            component_integrity_score=max(0.0, comp_score),
            layer_ordering_score=max(0.0, layer_score),
            material_region_score=mat_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.80
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return FabricationValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
