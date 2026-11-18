from typing import List, Dict, Any
from ..core.vas_types import ValidationMethod
from ..core.vas_schema import AcceptanceCriterion, ToleranceSpec

class CriteriaGenerator:
    @classmethod
    def generate_criteria(
        cls,
        dimensions: Dict[str, Any],
        silhouette: Dict[str, Any],
        materials: Dict[str, Any],
        tolerances: List[ToleranceSpec]
    ) -> List[AcceptanceCriterion]:
        criteria = []

        # 1. Criterio de Silueta Visual
        criteria.append(AcceptanceCriterion(
            criterion_id="CRIT_SILHOUETTE_SIMILARITY",
            target_property="visual_identity.silhouette_match",
            target_value=1.0,
            tolerance=0.10,
            priority=1.0,
            validation_method=ValidationMethod.VISUAL,
            minimum_score=0.90,
            failure_severity="BLOCKER"
        ))

        # 2. Criterios Dimensionales Numéricos
        for tol in tolerances:
            criteria.append(AcceptanceCriterion(
                criterion_id=f"CRIT_DIM_{tol.property_name.upper()}",
                target_property=f"dimensions.{tol.property_name}",
                target_value=tol.target_value,
                tolerance=tol.tolerance_value,
                priority=0.95,
                validation_method=ValidationMethod.NUMERIC,
                minimum_score=0.95,
                failure_severity="BLOCKER"
            ))

        # 3. Criterio de Identidad de Materiales
        if "base_material" in materials:
            criteria.append(AcceptanceCriterion(
                criterion_id="CRIT_MATERIAL_MATCH",
                target_property="material_requirements.base_material",
                target_value=materials["base_material"],
                tolerance=0.05,
                priority=0.90,
                validation_method=ValidationMethod.MATERIAL,
                minimum_score=0.85,
                failure_severity="MAJOR"
            ))

        # 4. Criterio de Integridad Topológica
        criteria.append(AcceptanceCriterion(
            criterion_id="CRIT_TOPOLOGY_MANIFOLD",
            target_property="geometry_requirements.is_manifold",
            target_value=True,
            tolerance=0.0,
            priority=1.0,
            validation_method=ValidationMethod.TOPOLOGICAL,
            minimum_score=1.0,
            failure_severity="BLOCKER"
        ))

        # 5. Criterio de Colisión Unreal Engine
        criteria.append(AcceptanceCriterion(
            criterion_id="CRIT_UNREAL_COLLISION",
            target_property="unreal_requirements.collision_present",
            target_value=True,
            tolerance=0.0,
            priority=0.85,
            validation_method=ValidationMethod.ENGINE,
            minimum_score=1.0,
            failure_severity="MAJOR"
        ))

        return criteria
