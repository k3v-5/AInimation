"""
StrategyEvaluator scores strategies and produces audit decision traces.
UAF-81.2 Sections 19, 24, 25, 27, 28, 29, 30.
"""

from typing import List, Optional, Tuple, Set
from ..strategies.generation_strategy import GenerationStrategy
from .strategy_score import StrategyScore, CandidateEvaluation, StrategyDecisionTrace
from ...intelligence.compiler.resolved_specification import ResolvedAssetSpecification
from ...capabilities.capability_registry import CapabilityRegistry


class StrategyEvaluator:
    """
    Multidimensional evaluator that ranks candidate strategies and explains rejection/acceptance.
    """
    @classmethod
    def evaluate_candidates(
        cls,
        spec: ResolvedAssetSpecification,
        candidates: List[GenerationStrategy],
        available_capabilities: Set[str],
    ) -> Tuple[Optional[GenerationStrategy], StrategyDecisionTrace]:
        trace = StrategyDecisionTrace(
            asset_id=spec.original_specification.identity.asset_id,
            target_profile=spec.effective_target_profile,
            quality_profile=spec.effective_quality_profile,
        )

        eligible_candidates: List[Tuple[GenerationStrategy, StrategyScore]] = []

        for strat in candidates:
            # 1. Hard requirement check: All strategy required_capabilities must be available
            missing_caps = [c for c in strat.required_capabilities if c not in available_capabilities]

            # Also verify if strategy covers what the spec required
            spec_missing = [c for c in spec.required_capabilities if c not in strat.required_capabilities and c not in strat.optional_capabilities]

            if missing_caps:
                trace.candidates.append(
                    CandidateEvaluation(
                        strategy_id=strat.strategy_id,
                        is_eligible=False,
                        missing_hard_capabilities=missing_caps,
                        rejection_reason=f"Engine lacks required capabilities: {', '.join(missing_caps)}",
                    )
                )
                continue

            if spec_missing:
                trace.candidates.append(
                    CandidateEvaluation(
                        strategy_id=strat.strategy_id,
                        is_eligible=False,
                        missing_hard_capabilities=spec_missing,
                        rejection_reason=f"Strategy does not satisfy required spec capabilities: {', '.join(spec_missing)}",
                    )
                )
                continue

            # Complexity compatibility check (Section 38)
            requested_complexity = spec.resolved_parameters.get("complexity") or spec.original_specification.parameters.get("complexity")
            if requested_complexity and strat.supported_complexities:
                if requested_complexity not in strat.supported_complexities:
                    trace.candidates.append(
                        CandidateEvaluation(
                            strategy_id=strat.strategy_id,
                            is_eligible=False,
                            rejection_reason=f"Strategy complexity {strat.supported_complexities} does not support requested complexity '{requested_complexity}'.",
                        )
                    )
                    continue


            # Compute multi-dimensional score
            score = StrategyScore(
                quality_score=strat.quality_rating,
                compatibility_score=1.0,
                reliability_score=0.9,
                determinism_score=1.0 if strat.determinism.value == "DETERMINISTIC" else 0.95,
                cost_score=strat.cost_rating,
                risk_score=strat.risk_rating,
                confidence=0.95,
            )

            trace.candidates.append(
                CandidateEvaluation(
                    strategy_id=strat.strategy_id,
                    is_eligible=True,
                    score=score,
                )
            )
            eligible_candidates.append((strat, score))

        if not eligible_candidates:
            trace.selected_strategy_id = None
            trace.selection_rationale = "No candidate strategy satisfied all hard capability requirements."
            return None, trace

        # Sort eligible candidates by aggregate_score descending
        eligible_candidates.sort(key=lambda item: item[1].aggregate_score, reverse=True)
        best_strat, best_score = eligible_candidates[0]

        trace.selected_strategy_id = best_strat.strategy_id
        trace.selection_rationale = (
            f"Selected '{best_strat.strategy_id}' with aggregate score {best_score.aggregate_score} "
            f"(quality={best_score.quality_score}, cost={best_score.cost_score})."
        )

        return best_strat, trace
