from typing import Dict, Any, List, Tuple
from ..core.spec_schema import AssetSpec, SpecDiffResult, ImpactAnalysisResult

class SpecDiffEngine:
    @staticmethod
    def compare_specs(old_spec: AssetSpec, new_spec: AssetSpec) -> SpecDiffResult:
        modified: Dict[str, Tuple[Any, Any]] = {}
        affected_subtrees: List[str] = []

        if old_spec.windows.count != new_spec.windows.count:
            modified["windows.count"] = (old_spec.windows.count, new_spec.windows.count)
            affected_subtrees.extend(["windows", "wall_geometry", "visual_validation"])

        if old_spec.door.width_m != new_spec.door.width_m:
            modified["door.width_m"] = (old_spec.door.width_m, new_spec.door.width_m)
            affected_subtrees.extend(["door", "collision", "interaction", "navigation"])

        if old_spec.visual.lean_angle_deg != new_spec.visual.lean_angle_deg:
            modified["visual.lean_angle_deg"] = (old_spec.visual.lean_angle_deg, new_spec.visual.lean_angle_deg)
            affected_subtrees.extend(["geometry", "transforms"])

        return SpecDiffResult(
            spec_id=new_spec.spec_id,
            old_version=old_spec.spec_version,
            new_version=new_spec.spec_version,
            modified_fields=modified,
            affected_subtrees=list(set(affected_subtrees))
        )

    @staticmethod
    def perform_impact_analysis(diff: SpecDiffResult) -> ImpactAnalysisResult:
        all_components = ["windows", "wall_geometry", "visual_validation", "door", "stairs", "player_interaction", "roof", "materials", "navigation"]
        affected = diff.affected_subtrees
        unaffected = [c for c in all_components if c not in affected]
        
        rebuild_scope = "SUBTREE" if len(affected) < len(all_components) else "FULL_ASSET"

        return ImpactAnalysisResult(
            affected_components=affected,
            unaffected_components=unaffected,
            rebuild_scope=rebuild_scope
        )
