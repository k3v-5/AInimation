from typing import Dict, Any, Tuple, List
from ...visual_intelligence.qa.quality_scorer import VerificationReport

class GoalEvaluator:
    def __init__(self, acceptance_threshold: float = 0.85):
        self.acceptance_threshold = acceptance_threshold

    def is_goal_satisfied(self, report: VerificationReport) -> Tuple[bool, str]:
        # 1. Comprobar Hard Constraints
        if len(report.hard_failures) > 0:
            return False, f"HARD_CONSTRAINT_FAILURE: {report.hard_failures}"

        # 2. Comprobar Good Enough Threshold
        if report.overall_score >= self.acceptance_threshold:
            return True, f"GOAL_ACHIEVED: Score {report.overall_score:.2f} >= threshold {self.acceptance_threshold:.2f} with 0 hard failures."

        return False, f"BELOW_THRESHOLD: Score {report.overall_score:.2f} < threshold {self.acceptance_threshold:.2f}."
