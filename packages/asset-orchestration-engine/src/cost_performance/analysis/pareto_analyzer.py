from typing import List, Dict, Any, Tuple

class ParetoAnalyzer:
    """Evaluates multi-objective candidate set and computes non-dominated Pareto front."""

    @staticmethod
    def classify_candidates(candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Objectives to maximize: quality_score
        Objectives to minimize: total_cost, runtime_cost, memory_mb, generation_time
        """
        non_dominated: List[Dict[str, Any]] = []
        dominated: List[Dict[str, Any]] = []

        for candidate in candidates:
            is_dominated = False
            for other in candidates:
                if candidate["candidate_id"] == other["candidate_id"]:
                    continue

                # 'other' dominates 'candidate' if it is >= in quality AND <= in cost & memory & time, with strictly better in at least one
                better_or_equal = (
                    other.get("quality_score", 0.0) >= candidate.get("quality_score", 0.0) and
                    other.get("total_cost", 100.0) <= candidate.get("total_cost", 100.0) and
                    other.get("memory_mb", 50.0) <= candidate.get("memory_mb", 50.0) and
                    other.get("generation_time", 30.0) <= candidate.get("generation_time", 30.0)
                )
                strictly_better = (
                    other.get("quality_score", 0.0) > candidate.get("quality_score", 0.0) or
                    other.get("total_cost", 100.0) < candidate.get("total_cost", 100.0) or
                    other.get("memory_mb", 50.0) < candidate.get("memory_mb", 50.0) or
                    other.get("generation_time", 30.0) < candidate.get("generation_time", 30.0)
                )
                if better_or_equal and strictly_better:
                    is_dominated = True
                    break

            if is_dominated:
                dominated.append(candidate)
            else:
                non_dominated.append(candidate)

        return non_dominated, dominated
