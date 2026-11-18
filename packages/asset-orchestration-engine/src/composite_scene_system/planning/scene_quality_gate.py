from typing import Dict, Any, List
from ..core.scene_schema import SceneBuildPlan, SceneDiagnosticReport
from ..core.scene_types import CollisionSeverity
from ..spatial.collision_validator import SceneCollisionValidator

class SceneQualityGate:
    @staticmethod
    def evaluate_scene(
        plan: SceneBuildPlan,
        roads: List[Dict[str, float]] = None
    ) -> SceneDiagnosticReport:
        layout_errors = []
        critical_errors = []
        collision_errors = []

        # 1. Comprobar colisiones
        raw_cols = SceneCollisionValidator.check_collisions(plan.instances, roads)
        for sev, msg in raw_cols:
            collision_errors.append(msg)
            if sev == CollisionSeverity.CRITICAL:
                critical_errors.append(msg)

        # 2. Comprobar presencia de landmarks obligatorios
        has_center = any(inst.region_id == "CENTER" for inst in plan.instances.values())
        if not has_center:
            layout_errors.append("MISSING_CENTER: Scene has no center landmark or plaza.")
            critical_errors.append("MISSING_CENTER")

        # 3. Puntuación ponderada
        # Layout 25%, Visual 25%, Technical 15%, Performance 10%, Gameplay 15%, Style 10%
        base_score = 1.00
        if collision_errors:
            base_score -= 0.30
        if layout_errors:
            base_score -= 0.20

        final_score = max(0.20, round(base_score, 2))
        is_valid = len(critical_errors) == 0 and final_score >= 0.85

        return SceneDiagnosticReport(
            scene_id=plan.scene_id,
            layout_errors=layout_errors,
            collision_errors=collision_errors,
            critical_errors=critical_errors,
            scene_quality_score=final_score,
            is_valid=is_valid
        )
