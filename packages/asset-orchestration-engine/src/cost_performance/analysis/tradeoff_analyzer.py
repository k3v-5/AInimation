from typing import Dict, Any

class TradeoffAnalyzer:
    """Generates structured tradeoff explanations comparing candidates against baseline."""

    @staticmethod
    def compare_tradeoff(baseline: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        base_q = baseline.get("quality_score", 0.90)
        cand_q = candidate.get("quality_score", 0.90)
        delta_q = (cand_q - base_q) / max(0.001, base_q) * 100.0

        base_mem = baseline.get("memory_mb", 20.0)
        cand_mem = candidate.get("memory_mb", 20.0)
        delta_mem = (cand_mem - base_mem) / max(0.001, base_mem) * 100.0

        base_time = baseline.get("generation_time", 30.0)
        cand_time = candidate.get("generation_time", 30.0)
        delta_time = (cand_time - base_time) / max(0.001, base_time) * 100.0

        base_cost = baseline.get("total_cost", 100.0)
        cand_cost = candidate.get("total_cost", 100.0)
        delta_cost = (cand_cost - base_cost) / max(0.001, base_cost) * 100.0

        explanation = (
            f"Candidate [{candidate.get('candidate_id', 'UNKNOWN')}]: "
            f"{'+' if delta_q >= 0 else ''}{delta_q:.1f}% quality, "
            f"{'+' if delta_mem >= 0 else ''}{delta_mem:.1f}% memory, "
            f"{'+' if delta_time >= 0 else ''}{delta_time:.1f}% generation time, "
            f"{'+' if delta_cost >= 0 else ''}{delta_cost:.1f}% total cost vs baseline."
        )

        return {
            "candidate_id": candidate.get("candidate_id"),
            "delta_quality_percent": round(delta_q, 2),
            "delta_memory_percent": round(delta_mem, 2),
            "delta_time_percent": round(delta_time, 2),
            "delta_cost_percent": round(delta_cost, 2),
            "explanation": explanation
        }
