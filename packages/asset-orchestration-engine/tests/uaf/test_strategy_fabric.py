"""
Tests for UAF-81.2 Capability and Generation Strategy Fabric:
Capabilities, Strategies, Implementations, Evaluator, Planner, and Replanner.
UAF-81.2 Sections 5, 16, 23, 27, 28, 29, 31, 32, 33, 34, 61, 83.
"""

import pytest
from uaf.core.identity.asset_types import AssetType
from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.specification.asset_specification import AssetSpecification
from uaf.strategy.capabilities.capability_contract import CapabilityType, CapabilityContract, ComprehensiveCapability
from uaf.strategy.strategies.strategy_category import StrategyCategory, DeterminismMode
from uaf.strategy.strategies.generation_strategy import GenerationStrategy
from uaf.strategy.strategies.strategy_registry import StrategyRegistry
from uaf.strategy.implementations.implementation import ExecutionBackend, ImplementationDescription
from uaf.strategy.implementations.implementation_registry import ImplementationRegistry
from uaf.strategy.evaluation.strategy_score import StrategyScore, CandidateEvaluation, StrategyDecisionTrace
from uaf.strategy.evaluation.strategy_evaluator import StrategyEvaluator
from uaf.strategy.planning.plan_node import GenerationPlanNode
from uaf.strategy.planning.generation_plan import GenerationPlan
from uaf.strategy.planning.generation_planner import GenerationPlanner
from uaf.strategy.planning.replanning import Replanner, ReplanRequest
from uaf.intelligence.compiler.resolution_pipeline import ResolutionPipeline


def test_capability_contract_and_descriptor():
    contract = CapabilityContract(
        input_schema={"type": "mesh"},
        output_schema={"type": "weights"},
        preconditions=["valid_skeleton", "compatible_mesh"],
        postconditions=["vertex_groups", "normalized_weights"],
    )
    cap = ComprehensiveCapability(
        capability_id="skin_weight_generation",
        name="Skin Weight Generator",
        capability_type=CapabilityType.SKINNING,
        contract=contract,
        limitations=["max_influences_4"],
        determinism="DETERMINISTIC",
    )
    assert cap.capability_type == CapabilityType.SKINNING
    assert "valid_skeleton" in cap.contract.preconditions
    data = cap.to_dict()
    assert data["capability_id"] == "skin_weight_generation"


def test_strategy_registry_queries():
    strat_reg = StrategyRegistry()
    assert strat_reg.supports("PrimitiveProceduralStrategy")
    assert strat_reg.supports("AdvancedHeroCharacterStrategy")

    char_strats = strat_reg.find_for_asset(AssetType.CHARACTER)
    assert len(char_strats) >= 3
    strat_ids = [s.strategy_id for s in char_strats]
    assert "PrimitiveProceduralStrategy" in strat_ids
    assert "AdvancedHeroCharacterStrategy" in strat_ids


def test_implementation_registry_and_discovery():
    imp_reg = ImplementationRegistry()
    organic_imps = imp_reg.find_for_capability("organic_surface_generation")
    assert len(organic_imps) >= 1
    assert organic_imps[0].capability_id == "organic_surface_generation"
    assert organic_imps[0].backend_type == ExecutionBackend.IN_PROCESS


def test_strategy_evaluator_scoring():
    score = StrategyScore(
        quality_score=0.9,
        compatibility_score=1.0,
        reliability_score=0.9,
        determinism_score=1.0,
        cost_score=0.4,
        risk_score=0.1,
    )
    # Benefit sum - penalty sum
    # (0.9*0.35 + 1.0*0.25 + 0.9*0.15 + 1.0*0.10) - (0.4*0.10 + 0.1*0.05)
    # (0.315 + 0.25 + 0.135 + 0.10) - (0.04 + 0.005) = 0.80 - 0.045 = 0.755
    assert pytest.approx(score.aggregate_score, 0.001) == 0.755


def test_replanner_applies_fallback_with_degradation_logging():
    """
    CRITICAL INVARIANT (Section 34):
    Fallback must explicitly record degradation without silent quality loss.
    """
    node = GenerationPlanNode(
        node_id="face_synth",
        operation="GENERATE",
        capability="advanced_facial_generation",
        implementation="FacialMeshSynthesisV2",
        fallbacks=["FacialMeshSynthesisV1_LowPoly"],
    )
    plan = GenerationPlan(
        plan_id="plan_test_01",
        asset_id="char_hero",
        strategy_id="AdvancedHeroCharacterStrategy",
        specification_hash="hash_spec_123",
        nodes={"face_synth": node},
        execution_order=["face_synth"],
        expected_quality=0.95,
    )

    request = ReplanRequest(
        failed_node_id="face_synth",
        failure_reason="Out of VRAM on high-res neural facial pass",
        current_plan=plan,
    )

    result = Replanner.replan(request)
    assert result.is_success is True
    assert result.updated_plan is not None

    # Verify new implementation is the fallback
    updated_node = result.updated_plan.nodes["face_synth"]
    assert updated_node.implementation == "FacialMeshSynthesisV1_LowPoly"

    # Verify degradation report was generated (Section 34)
    deg = result.degradation_report
    assert deg is not None
    assert deg["failed_implementation"] == "FacialMeshSynthesisV2"
    assert deg["fallback_implementation"] == "FacialMeshSynthesisV1_LowPoly"
    assert "Out of VRAM" in deg["reason"]
    assert result.updated_plan.expected_quality < plan.expected_quality
