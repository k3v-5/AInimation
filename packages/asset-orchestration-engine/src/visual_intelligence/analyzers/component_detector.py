from typing import List, Tuple, Dict, Any
from ..core.visual_goal_builder import VisualGoalSpec

class ComponentDetector:
    @staticmethod
    def detect_components(
        present_components: List[str],
        goal: VisualGoalSpec
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        pres_set = set(present_components)
        req_set = set(goal.required_components)
        forb_set = set(goal.forbidden_components)

        missing = list(req_set - pres_set)
        forbidden_found = list(pres_set.intersection(forb_set))

        failures = []
        if missing:
            failures.append(f"MISSING_REQUIRED_COMPONENTS: {missing}")
        if forbidden_found:
            failures.append(f"FORBIDDEN_COMPONENTS_DETECTED: {forbidden_found}")

        evidence = {
            "present_components": present_components,
            "missing_required": missing,
            "forbidden_found": forbidden_found
        }

        if missing or forbidden_found:
            score = max(0.0, round(1.0 - (len(missing) * 0.3) - (len(forbidden_found) * 0.4), 4))
        else:
            score = 1.0

        return score, evidence, failures
