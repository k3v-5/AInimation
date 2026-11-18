from typing import Dict, Any, Tuple
from ..core.production_job import ProductionJob

class BudgetEnforcer:
    """Enforces execution limits (time, blender runs, memory, correction attempts)."""

    @staticmethod
    def validate_job_budget(job: ProductionJob, elapsed_time: float, current_corrections: int) -> Tuple[bool, str]:
        max_time = job.budget.get("max_execution_time", 180.0)
        if elapsed_time > max_time:
            return False, f"BUDGET_EXCEEDED: Elapsed time {elapsed_time:.1f}s exceeded max {max_time:.1f}s"

        max_corrections = job.budget.get("max_correction_iterations", 3)
        if current_corrections > max_corrections:
            return False, f"BUDGET_EXCEEDED: Correction iterations {current_corrections} exceeded limit {max_corrections}"

        return True, "Within budget limits"
