from typing import Dict, Any, List, Optional, Tuple

from ..core.cost_models import CostReport, CostMetric, MeasurementMethod
from ..core.performance_models import PerformanceReport
from ..core.quality_floor import QualityFloor
from ..core.optimization_profiles import OptimizationProfile, ProfileType
from ..core.budget_models import BudgetLimits, BudgetStatus
from ..analysis.cost_evaluator import CostEvaluator
from ..analysis.performance_evaluator import PerformanceEvaluator
from ..analysis.pareto_analyzer import ParetoAnalyzer
from ..analysis.tradeoff_analyzer import TradeoffAnalyzer
from ..analysis.budget_checker import BudgetChecker
from ..candidates.candidate_models import CandidateStrategy, CandidateStatus
from ..candidates.geometry_optimizer import GeometryOptimizer
from ..candidates.material_optimizer import MaterialOptimizer
from ..candidates.texture_optimizer import TextureOptimizer
from ..candidates.lod_optimizer import LODOptimizer
from ..candidates.collision_optimizer import CollisionOptimizer
from ..planning.optimization_plan import OptimizationPlan
from ..planning.plan_builder import PlanBuilder
from ..planning.lifecycle_controller import LifecycleController, LifecycleStage
from ..persistence.audit_trail import AuditRecord
from ..persistence.cost_performance_store import CostPerformanceStore

from ..integration.governance_bridge import GovernanceBridge
from ..integration.knowledge_graph_bridge import KnowledgeGraphBridge
from ..integration.benchmark_bridge import BenchmarkBridge
from ..integration.golden_asset_bridge import GoldenAssetBridge
from ..integration.failure_analysis_bridge import FailureAnalysisBridge
from ..integration.strategy_learning_bridge import StrategyLearningBridge
from ..integration.recovery_bridge import RecoveryBridge
from ..integration.readiness_bridge import ReadinessBridge

from ...evaluation import EvaluationBenchmarkAPI
from ...golden import GoldenAPI
from ...failure_analysis import FailureAnalysisAPI
from ...strategy_learning import StrategyLearningAPI

class CostPerformanceAPI:
    """
    Unified public API for Phase 79: Cost/Performance Optimizer System.
    """
    def __init__(
        self,
        persistence_path: Optional[str] = None,
        eval_api: Optional[EvaluationBenchmarkAPI] = None,
        golden_api: Optional[GoldenAPI] = None,
        failure_api: Optional[FailureAnalysisAPI] = None,
        strat_api: Optional[StrategyLearningAPI] = None
    ):
        self.store = CostPerformanceStore(persistence_path)
        self.eval_bridge = BenchmarkBridge(eval_api)
        self.golden_bridge = GoldenAssetBridge(golden_api)
        self.failure_bridge = FailureAnalysisBridge(failure_api)
        self.strat_bridge = StrategyLearningBridge(strat_api)
        self.gov_bridge = GovernanceBridge()
        self.kg_bridge = KnowledgeGraphBridge()
        self.recovery_bridge = RecoveryBridge()
        self.readiness_bridge = ReadinessBridge()

    def evaluate_cost(self, metrics: Dict[str, Any]) -> CostReport:
        return CostEvaluator.evaluate(metrics)

    def evaluate_performance(self, metrics: Dict[str, Any]) -> PerformanceReport:
        return PerformanceEvaluator.evaluate(metrics)

    def check_budgets(self, limits: BudgetLimits, candidate_metrics: Dict[str, Any]) -> Tuple[BudgetStatus, Dict[str, BudgetStatus]]:
        return BudgetChecker.check_budgets(limits, candidate_metrics)

    def build_pareto_front(self, candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        return ParetoAnalyzer.classify_candidates(candidates)

    def compare_strategies(self, baseline: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        return TradeoffAnalyzer.compare_tradeoff(baseline, candidate)

    def create_optimization_plan(
        self,
        plan_id: str,
        semantic_id: str,
        baseline: Dict[str, Any],
        candidates: List[CandidateStrategy],
        profile: Optional[OptimizationProfile] = None,
        floor: Optional[QualityFloor] = None,
        budgets: Optional[BudgetLimits] = None
    ) -> OptimizationPlan:
        plan = PlanBuilder.build_plan(
            plan_id=plan_id,
            semantic_id=semantic_id,
            baseline=baseline,
            candidates=candidates,
            profile=profile,
            floor=floor,
            budgets=budgets
        )
        self.store.store_plan(plan.plan_id, plan.to_dict())
        if plan.selected_strategy_id:
            sel = next(c for c in candidates if c.candidate_id == plan.selected_strategy_id)
            self.kg_bridge.record_optimization_node(plan.plan_id, semantic_id, plan.selected_strategy_id, sel.quality_score)
        return plan

    def apply_optimization(
        self,
        plan: OptimizationPlan,
        agent_id: str = "agent.optimizer"
    ) -> Tuple[bool, str]:
        # Governance authorization check
        allowed, msg = self.gov_bridge.check_optimization_permission(agent_id, ["CAP_GEOMETRY", "CAP_BLENDER"])
        if not allowed:
            return False, f"GOVERNANCE_DENIED: {msg}"

        if not plan.selected_strategy_id:
            return False, "No valid strategy selected in optimization plan"

        controller = LifecycleController(plan)
        controller.advance_to_apply()
        return True, f"Optimization '{plan.selected_strategy_id}' applied successfully"

    def validate_optimization(
        self,
        plan: OptimizationPlan,
        actual_score: float
    ) -> Tuple[bool, str]:
        # Check against Golden Assets for regression
        is_reg, delta = self.golden_bridge.check_regression(plan.asset_semantic_id, actual_score)
        if is_reg:
            return False, f"REGRESSION_DETECTED: Delta {delta:.4f} against Golden Asset baseline"

        # Check against Quality floor
        passed_floor, reason = plan.quality_floor.evaluate({"overall_quality": actual_score})
        if not passed_floor:
            return False, f"QUALITY_FLOOR_VIOLATION: {reason}"

        return True, "Optimization validated successfully"

    def commit_optimization(
        self,
        plan: OptimizationPlan,
        agent_id: str = "agent.optimizer"
    ) -> bool:
        controller = LifecycleController(plan)
        controller.commit()
        self.store.store_plan(plan.plan_id, plan.to_dict())

        # Record audit
        audit = AuditRecord(
            optimization_id=plan.plan_id,
            asset_id=plan.asset_semantic_id,
            baseline_id=plan.baseline.get("candidate_id", "BASELINE"),
            profile=plan.optimization_profile.profile_type.value,
            selected_candidate_id=plan.selected_strategy_id,
            rejected_candidate_ids=plan.rejected_strategy_ids,
            rejection_reasons=plan.rejection_reasons,
            is_committed=True,
            is_rolled_back=False
        )
        self.store.record_audit(audit)
        return True

    def rollback_optimization(
        self,
        plan: OptimizationPlan,
        reason: str = "Validation failure"
    ) -> bool:
        controller = LifecycleController(plan)
        controller.rollback(reason)
        self.store.store_plan(plan.plan_id, plan.to_dict())

        audit = AuditRecord(
            optimization_id=plan.plan_id,
            asset_id=plan.asset_semantic_id,
            baseline_id=plan.baseline.get("candidate_id", "BASELINE"),
            profile=plan.optimization_profile.profile_type.value,
            selected_candidate_id=plan.selected_strategy_id,
            rejected_candidate_ids=plan.rejected_strategy_ids,
            rejection_reasons=plan.rejection_reasons,
            is_committed=False,
            is_rolled_back=True
        )
        self.store.record_audit(audit)
        return True

    def optimize_asset(
        self,
        semantic_id: str,
        baseline: Dict[str, Any],
        candidates: List[CandidateStrategy],
        profile: Optional[OptimizationProfile] = None,
        floor: Optional[QualityFloor] = None,
        budgets: Optional[BudgetLimits] = None,
        agent_id: str = "agent.optimizer"
    ) -> OptimizationPlan:
        plan_id = f"PLAN_OPT_{semantic_id.replace('.', '_')}"
        plan = self.create_optimization_plan(plan_id, semantic_id, baseline, candidates, profile, floor, budgets)
        applied, msg = self.apply_optimization(plan, agent_id=agent_id)
        if applied and plan.selected_strategy_id:
            sel_cand = next(c for c in candidates if c.candidate_id == plan.selected_strategy_id)
            valid, val_msg = self.validate_optimization(plan, sel_cand.quality_score)
            if valid:
                self.commit_optimization(plan, agent_id=agent_id)
            else:
                self.rollback_optimization(plan, reason=val_msg)
        return plan
