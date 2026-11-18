from typing import Dict, Any, Tuple, List
from ..core.visual_goal_builder import VisualGoalSpec

class ProportionAnalyzer:
    @staticmethod
    def analyze_proportions(
        component_dimensions: Dict[str, Tuple[float, float, float]],
        goal: VisualGoalSpec
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        """
        Calcula ratios de proporción relativos y devuelve (score, evidence_dict, failure_list).
        """
        total_len = sum(dim[2] for dim in component_dimensions.values())
        if total_len <= 0.0:
            return 0.0, {}, ["TOTAL_LENGTH_ZERO"]

        blade_dim = component_dimensions.get("blade", (0, 0, 0))
        actual_blade_ratio = round(blade_dim[2] / total_len, 4)

        target_cfg = goal.target_proportions.get("blade_ratio", {"target": 0.72, "min": 0.65, "max": 0.78})
        t_target = target_cfg["target"]
        t_min = target_cfg["min"]
        t_max = target_cfg["max"]

        evidence = {
            "measured_blade_ratio": actual_blade_ratio,
            "target": t_target,
            "min": t_min,
            "max": t_max
        }

        failures = []
        if actual_blade_ratio < t_min or actual_blade_ratio > t_max:
            failures.append(f"BLADE_RATIO_OUT_OF_RANGE: actual {actual_blade_ratio:.2f} vs expected [{t_min:.2f}-{t_max:.2f}] (target {t_target:.2f})")
            diff = abs(actual_blade_ratio - t_target)
            score = max(0.0, round(1.0 - (diff * 2.0), 4))
        else:
            diff = abs(actual_blade_ratio - t_target)
            score = max(0.85, round(1.0 - diff, 4))

        return score, evidence, failures
