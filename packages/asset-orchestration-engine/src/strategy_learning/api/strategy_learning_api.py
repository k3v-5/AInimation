from typing import Dict, Any, List, Optional, Tuple

from ..core.strategy_models import StrategyRecord, StrategyStatus
from ..core.learning_models import StrategyOutcome, LearningEvent, StrategyOptimizationProfile
from ..core.feature_models import ProblemFeatures, FeatureExtractor
from ..core.strategy_signatures import ProblemSignature, StrategySignature
from ..history.strategy_history import StrategyHistory
from ..history.outcome_history import OutcomeHistory
from ..history.execution_history import ExecutionHistory
from ..analysis.strategy_analyzer import StrategyAnalyzer
from ..analysis.success_analyzer import SuccessAnalyzer
from ..analysis.failure_analyzer import FailureAnalyzer
from ..analysis.cost_analyzer import CostAnalyzer
from ..analysis.regression_analyzer import RegressionAnalyzer
from ..ranking.candidate_scorer import CandidateScorer
from ..ranking.confidence_engine import ConfidenceEngine
from ..ranking.exploration_policy import ExplorationPolicy
from ..ranking.strategy_ranker import StrategyRanker
from ..optimization.tradeoff_optimizer import TradeoffOptimizer
from ..optimization.parameter_optimizer import ParameterOptimizer
from ..optimization.constraint_optimizer import ConstraintOptimizer
from ..optimization.strategy_optimizer import StrategyOptimizer
from ..learning.outcome_learner import OutcomeLearner
from ..learning.pattern_learner import PatternLearner
from ..learning.transfer_learning import TransferLearning
from ..learning.learning_engine import LearningEngine
from ..safety.learning_guard import LearningGuard
from ..safety.strategy_guard import StrategyGuard, RegressionGuard
from ..integration.orchestration_bridge import OrchestrationBridge
from ..integration.context_memory_bridge import ContextMemoryBridge
from ..integration.knowledge_graph_bridge import KnowledgeGraphBridge
from ..integration.benchmark_bridge import BenchmarkBridge
from ..integration.golden_asset_bridge import GoldenAssetBridge
from ..integration.failure_analysis_bridge import FailureAnalysisBridge
from ..persistence.strategy_learning_store import StrategyLearningStore

from ...evaluation import EvaluationBenchmarkAPI
from ...golden import GoldenAPI
from ...failure_analysis import FailureAnalysisAPI

class StrategyLearningAPI:
    """
    Unified public API for Phase 78: Strategy Learning & Optimization System.
    """
    def __init__(
        self,
        persistence_path: Optional[str] = None,
        eval_api: Optional[EvaluationBenchmarkAPI] = None,
        golden_api: Optional[GoldenAPI] = None,
        failure_api: Optional[FailureAnalysisAPI] = None
    ):
        self.store = StrategyLearningStore(persistence_path)
        self.history = StrategyHistory()
        self.outcome_history = OutcomeHistory()
        self.execution_history = ExecutionHistory()

        self.eval_bridge = BenchmarkBridge(eval_api)
        self.golden_bridge = GoldenAssetBridge(golden_api)
        self.failure_bridge = FailureAnalysisBridge(failure_api)
        self.kg_bridge = KnowledgeGraphBridge()
        self.memory_bridge = ContextMemoryBridge()
        self.orch_bridge = OrchestrationBridge()

        # Ingest stored strategies and outcomes
        for s in self.store.list_strategies():
            self.history.register_strategy(s)
        for o in self.store.list_outcomes():
            self.outcome_history.record_outcome(o)

    def register_strategy(self, strategy: StrategyRecord) -> StrategyRecord:
        if not strategy.strategy_signature:
            strategy.strategy_signature = StrategySignature.compute(strategy.to_dict())
        self.store.store_strategy(strategy)
        self.history.register_strategy(strategy)
        self.kg_bridge.record_strategy_node(strategy.strategy_id, strategy.asset_type, strategy.average_quality_score)
        return strategy

    def get_strategy(self, strategy_id: str) -> Optional[StrategyRecord]:
        return self.history.get_strategy(strategy_id)

    def list_strategies(self, asset_type: Optional[str] = None) -> List[StrategyRecord]:
        return self.history.list_strategies(asset_type)

    def extract_features(self, request_data: Dict[str, Any]) -> ProblemFeatures:
        return FeatureExtractor.extract(request_data)

    def build_problem_signature(self, features: ProblemFeatures) -> str:
        return ProblemSignature.compute(features)

    def record_outcome(self, outcome: StrategyOutcome) -> StrategyOutcome:
        valid, msg = LearningGuard.is_outcome_valid_for_learning(outcome)
        self.store.store_outcome(outcome)
        self.outcome_history.record_outcome(outcome)

        # Incrementally update strategy performance if strategy exists
        strat = self.get_strategy(outcome.strategy_id)
        if strat and valid:
            evt = LearningEngine.process_outcome(strat, outcome)
            self.store.store_strategy(strat)
            self.history.update_strategy(strat)
            self.store.store_event(evt)

        return outcome

    def analyze_strategy(self, strategy_id: str) -> Dict[str, Any]:
        strat = self.get_strategy(strategy_id)
        if not strat:
            raise KeyError(f"Strategy {strategy_id} not found.")
        outcomes = self.outcome_history.get_outcomes_for_strategy(strategy_id)
        return StrategyAnalyzer.analyze_strategy(strat, outcomes)

    def rank_strategies(
        self,
        strategies: Optional[List[StrategyRecord]] = None,
        profile: Optional[StrategyOptimizationProfile] = None
    ) -> List[Tuple[StrategyRecord, float]]:
        strats = strategies if strategies is not None else self.list_strategies()
        return StrategyRanker.rank(strats, profile)

    def recommend_strategy(
        self,
        features: Optional[ProblemFeatures] = None,
        profile: Optional[StrategyOptimizationProfile] = None,
        deterministic: bool = True
    ) -> StrategyRecord:
        strats = self.list_strategies()
        if not strats:
            raise ValueError("No strategies registered in system.")

        # Filter against hard constraints if features provided
        if features:
            valid_strats = [s for s in strats if ConstraintOptimizer.validate_constraints(s, features)]
            if valid_strats:
                strats = valid_strats

        ranked = StrategyRanker.rank(strats, profile)
        ranked_strats = [item[0] for item in ranked]
        prof = profile or StrategyOptimizationProfile.balanced()
        return ExplorationPolicy.select_strategy(ranked_strats, prof, deterministic=deterministic)

    def optimize_strategy(
        self,
        base_strategy_id: str,
        param_deltas: Dict[str, Any],
        change_reason: str = "Performance optimization"
    ) -> StrategyRecord:
        base = self.get_strategy(base_strategy_id)
        if not base:
            raise KeyError(f"Base strategy {base_strategy_id} not found.")

        new_strat = StrategyOptimizer.derive_optimized_version(base, param_deltas, change_reason)
        return self.register_strategy(new_strat)

    def optimize_parameters(self, configurations: List[Dict[str, Any]], param_name: str) -> Any:
        return ParameterOptimizer.recommend_best_parameter(configurations, param_name)

    def compare_strategies(
        self,
        strategy_a_id: str,
        strategy_b_id: str
    ) -> Dict[str, Any]:
        a = self.get_strategy(strategy_a_id)
        b = self.get_strategy(strategy_b_id)
        if not a or not b:
            raise KeyError("One or both strategies not found.")

        delta_quality = a.average_quality_score - b.average_quality_score
        delta_cost = a.estimated_cost - b.estimated_cost
        delta_time = a.estimated_time - b.estimated_time

        winner = a.strategy_id if a.average_quality_score >= b.average_quality_score else b.strategy_id

        return {
            "strategy_a": a.strategy_id,
            "strategy_b": b.strategy_id,
            "quality_a": a.average_quality_score,
            "quality_b": b.average_quality_score,
            "delta_quality": round(delta_quality, 4),
            "delta_cost": round(delta_cost, 4),
            "delta_time": round(delta_time, 4),
            "winner": winner
        }

    def get_pareto_front(self, strategies: Optional[List[StrategyRecord]] = None) -> List[StrategyRecord]:
        strats = strategies if strategies is not None else self.list_strategies()
        return TradeoffOptimizer.compute_pareto_front(strats)

    def learn_from_outcome(self, outcome: StrategyOutcome) -> StrategyOutcome:
        return self.record_outcome(outcome)

    def find_similar_cases(self, asset_class: str) -> List[StrategyRecord]:
        return [s for s in self.list_strategies() if s.asset_class == asset_class]

    def get_strategy_history(self, strategy_id: str) -> List[StrategyOutcome]:
        return self.outcome_history.get_outcomes_for_strategy(strategy_id)

    def get_learning_statistics(self) -> Dict[str, Any]:
        all_outcomes = self.outcome_history.list_all()
        return {
            "total_strategies": len(self.list_strategies()),
            "total_outcomes": len(all_outcomes),
            "success_rate": round(sum(1 for o in all_outcomes if o.success) / len(all_outcomes), 4) if all_outcomes else 1.0,
            "total_learning_events": len(self.store.list_events())
        }
