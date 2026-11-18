import time
from typing import Dict, Any, List, Optional
from .optimization_plan import OptimizationPlan
from ..candidates.candidate_models import CandidateStrategy, CandidateStatus
from ..core.quality_floor import QualityFloor
from ..core.optimization_profiles import OptimizationProfile
from ..core.budget_models import BudgetLimits, BudgetStatus
from ..analysis.pareto_analyzer import ParetoAnalyzer
from ..analysis.tradeoff_analyzer import TradeoffAnalyzer
from ..analysis.budget_checker import BudgetChecker

class PlanBuilder:
    """Builds a complete, verifiable OptimizationPlan from candidates, profile and baseline."""

    @staticmethod
    def build_plan(
        plan_id: str,
        semantic_id: str,
        baseline: Dict[str, Any],
        candidates: List[CandidateStrategy],
        profile: Optional[OptimizationProfile] = None,
        floor: Optional[QualityFloor] = None,
        budgets: Optional[BudgetLimits] = None
    ) -> OptimizationPlan:
        prof = profile or OptimizationProfile.balanced()
        q_floor = floor or QualityFloor()
        b_limits = budgets or BudgetLimits()

        rejected_ids: List[str] = []
        rejection_reasons: Dict[str, str] = {}
        approved_candidates: List[CandidateStrategy] = []

        # 1. Quality Floor & Budget Verification
        for cand in candidates:
            cand_dict = cand.to_dict()
            passed_floor, floor_reason = q_floor.evaluate({
                "overall_quality": cand.quality_score,
                "visual": cand.visual_score,
                "geometry": cand.geometry_score,
                "engine_readiness": cand.engine_readiness_score,
                "regression_delta": cand_dict.get("regression_delta", 0.0)
            })

            if not passed_floor:
                cand.status = CandidateStatus.REJECTED
                cand.rejection_reason = floor_reason
                rejected_ids.append(cand.candidate_id)
                rejection_reasons[cand.candidate_id] = floor_reason
                continue

            # Check budgets
            overall_b, b_breakdown = b_limits.check({
                "polygon_count": cand.target_polygon_budget,
                "material_count": cand.target_material_budget,
                "texture_memory_mb": cand.performance_report.texture_memory_mb,
                "generation_time": cand.cost_report.generation_time
            })
            cand.budget_status = overall_b

            if overall_b == BudgetStatus.OVER_BUDGET:
                cand.status = CandidateStatus.REJECTED
                reason = "Exceeded hard budget constraints"
                cand.rejection_reason = reason
                rejected_ids.append(cand.candidate_id)
                rejection_reasons[cand.candidate_id] = reason
                continue

            # Calculate Optimization Score under profile
            cost_norm = max(0.0, 1.0 - (cand.cost_report.total_cost / 300.0))
            perf_norm = max(0.0, 1.0 - (cand.target_polygon_budget / 30000.0))
            mem_norm = max(0.0, 1.0 - (cand.performance_report.asset_memory_estimate_mb / 64.0))
            time_norm = max(0.0, 1.0 - (cand.cost_report.generation_time / 120.0))

            cand.optimization_score = prof.calculate_score(
                quality_val=cand.quality_score,
                cost_norm=cost_norm,
                perf_norm=perf_norm,
                memory_norm=mem_norm,
                time_norm=time_norm,
                risk_val=cand.cost_report.failure_risk
            )
            cand.status = CandidateStatus.EVALUATED
            approved_candidates.append(cand)

        # 2. Pareto Front Analysis
        cand_dicts = [c.to_dict() for c in approved_candidates]
        non_dom, dom = ParetoAnalyzer.classify_candidates(cand_dicts)
        pareto_ids = [c["candidate_id"] for c in non_dom]

        for cand in approved_candidates:
            cand.is_pareto_optimal = cand.candidate_id in pareto_ids

        # 3. Strategy Selection
        selected_id = None
        if approved_candidates:
            # Pick highest optimization score among approved candidates
            best_cand = max(approved_candidates, key=lambda c: c.optimization_score)
            best_cand.status = CandidateStatus.SELECTED
            selected_id = best_cand.candidate_id

        # 4. Compute Expected Tradeoff Delta vs Baseline
        expected_delta = {}
        if selected_id:
            sel_cand = next(c for c in approved_candidates if c.candidate_id == selected_id)
            expected_delta = TradeoffAnalyzer.compare_tradeoff(baseline, sel_cand.to_dict())

        return OptimizationPlan(
            plan_id=plan_id,
            asset_semantic_id=semantic_id,
            baseline=baseline,
            candidate_strategies=candidates,
            quality_floor=q_floor,
            optimization_profile=prof,
            budget_limits=b_limits,
            pareto_front_ids=pareto_ids,
            selected_strategy_id=selected_id,
            rejected_strategy_ids=rejected_ids,
            rejection_reasons=rejection_reasons,
            expected_delta=expected_delta,
            confidence=0.92
        )
