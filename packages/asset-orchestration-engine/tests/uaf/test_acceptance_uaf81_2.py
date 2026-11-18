"""
UAF-81.2 Acceptance Tests (Sections 90, 91, 92).
Verifies:
- Section 91 Critical Acceptance Test: Selection of Generator_B (advanced) over Generator_A (simple),
  and fail-early rejection with CapabilityGapReport if Generator_B is missing (NO SILENT DOWNGRADE).
- Section 92 Character Acceptance Test: C1, C3, and C4 strategy matrix progression.
"""

from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.identity.asset_types import AssetType
from uaf.core.specification.asset_specification import AssetSpecification
from uaf.intelligence.compiler.resolution_pipeline import ResolutionPipeline
from uaf.strategy.strategies.strategy_category import StrategyCategory, DeterminismMode
from uaf.strategy.strategies.generation_strategy import GenerationStrategy
from uaf.strategy.strategies.strategy_registry import StrategyRegistry
from uaf.strategy.implementations.implementation import ExecutionBackend, ImplementationDescription
from uaf.strategy.implementations.implementation_registry import ImplementationRegistry
from uaf.strategy.planning.generation_planner import GenerationPlanner


def test_critical_acceptance_section_91_generator_selection_and_gap():
    """
    Acceptance Test Section 91:
    - Generator_A provides simple_geometry
    - Generator_B provides advanced_geometry
    - Specification requiring advanced_geometry must select Generator_B.
    - If Generator_B is unavailable: CapabilityGapReport indicates failure (NO SILENT DOWNGRADE to Generator_A).
    """
    # 1. Custom strategy registry with Strategy A (simple) and Strategy B (advanced)
    strat_reg = StrategyRegistry()
    strat_reg.clear()

    strategy_a = GenerationStrategy(
        strategy_id="Strategy_Simple_A",
        name="Simple Geometry Strategy",
        category=StrategyCategory.PROCEDURAL,
        supported_assets=[AssetType.PROP],
        required_capabilities=["simple_geometry"],
        quality_rating=0.4,
        cost_rating=0.2,
        pipeline_node_templates=[{"node_id": "mesh_simple", "capability": "simple_geometry"}],
    )
    strategy_b = GenerationStrategy(
        strategy_id="Strategy_Advanced_B",
        name="Advanced Geometry Strategy",
        category=StrategyCategory.HYBRID,
        supported_assets=[AssetType.PROP],
        required_capabilities=["advanced_geometry"],
        quality_rating=0.9,
        cost_rating=0.7,
        pipeline_node_templates=[{"node_id": "mesh_advanced", "capability": "advanced_geometry"}],
    )

    strat_reg.register("Strategy_Simple_A", strategy_a)
    strat_reg.register("Strategy_Advanced_B", strategy_b)

    # 2. Implementation registry with both Generator_A and Generator_B
    imp_reg = ImplementationRegistry()
    imp_reg.clear()

    gen_a = ImplementationDescription(
        implementation_id="Generator_A",
        capability_id="simple_geometry",
        backend_type=ExecutionBackend.IN_PROCESS,
    )
    gen_b = ImplementationDescription(
        implementation_id="Generator_B",
        capability_id="advanced_geometry",
        backend_type=ExecutionBackend.IN_PROCESS,
    )

    imp_reg.register("Generator_A", gen_a)
    imp_reg.register("Generator_B", gen_b)

    planner = GenerationPlanner(strategy_registry=strat_reg, implementation_registry=imp_reg)
    pipeline = ResolutionPipeline()

    # Spec that requires advanced_geometry
    spec = AssetSpecification(
        identity=AssetIdentity(asset_id="hero_prop_01", asset_type=AssetType.PROP),
        quality_profile="hero",
        parameters={
            "complexity": "C4",
        },
    )
    # Mock resolved spec with required_capabilities=["advanced_geometry"]
    resolved_spec = pipeline.resolve(spec)
    # Explicitly require advanced_geometry on this spec
    object.__setattr__(resolved_spec, "required_capabilities", ["advanced_geometry"])

    # CASE 1: Both generators available -> Planner must select Strategy_Advanced_B with Generator_B
    res1 = planner.plan(resolved_spec)
    assert res1.is_success is True
    assert res1.plan is not None
    assert res1.plan.strategy_id == "Strategy_Advanced_B"
    assert res1.plan.nodes["mesh_advanced"].implementation == "Generator_B"

    # CASE 2: Generator_B is removed/unavailable -> Planner must NOT silently degrade to Generator_A!
    imp_reg_only_a = ImplementationRegistry()
    imp_reg_only_a.clear()
    imp_reg_only_a.register("Generator_A", gen_a)

    planner_only_a = GenerationPlanner(strategy_registry=strat_reg, implementation_registry=imp_reg_only_a)
    res2 = planner_only_a.plan(resolved_spec)

    # Must fail early and return gap report
    assert res2.is_success is False
    assert res2.gap_report is not None
    assert "advanced_geometry" in res2.gap_report.missing_capabilities
    assert "NO_VALID_STRATEGY" in res2.error_message


def test_character_acceptance_section_92_matrix():
    """
    Acceptance Test Section 92:
    Demonstrates strategy progression:
    - C1 Character -> Parametric/Primitive Strategy
    - C3 Character -> Hybrid Strategy
    - C4 Character -> Advanced Hero Character Strategy
    """
    planner = GenerationPlanner()
    pipeline = ResolutionPipeline()

    # Test C1
    spec_c1 = AssetSpecification(
        identity=AssetIdentity(asset_id="char_c1", asset_type=AssetType.CHARACTER),
        parameters={"complexity": "C1", "archetype": "HumanoidCharacter"},
    )
    resolved_c1 = pipeline.resolve(spec_c1)
    # C1 only needs basic capabilities
    object.__setattr__(resolved_c1, "required_capabilities", ["parametric_anatomy", "basic_rigging"])
    res_c1 = planner.plan(resolved_c1)
    assert res_c1.is_success is True
    assert res_c1.plan.strategy_id == "ParametricHumanoidStrategy"

    # Test C3
    spec_c3 = AssetSpecification(
        identity=AssetIdentity(asset_id="char_c3", asset_type=AssetType.CHARACTER),
        parameters={"complexity": "C3", "archetype": "HumanoidCharacter"},
    )
    resolved_c3 = pipeline.resolve(spec_c3)
    object.__setattr__(
        resolved_c3,
        "required_capabilities",
        ["organic_surface_generation", "skeletal_rigging", "cloth_geometry"],
    )
    res_c3 = planner.plan(resolved_c3)
    assert res_c3.is_success is True
    assert res_c3.plan.strategy_id == "HybridCharacterStrategy"

    # Test C4
    spec_c4 = AssetSpecification(
        identity=AssetIdentity(asset_id="char_c4", asset_type=AssetType.CHARACTER),
        parameters={
            "complexity": "C4",
            "archetype": "HumanoidCharacter",
            "facial_fidelity": "high",
            "clothing_complexity": "high",
        },
    )
    resolved_c4 = pipeline.resolve(spec_c4)
    res_c4 = planner.plan(resolved_c4)
    assert res_c4.is_success is True
    assert res_c4.plan.strategy_id == "AdvancedHeroCharacterStrategy"
    assert len(res_c4.plan.nodes) == 5  # anatomy, face, cloth, surface_detail, rig
    assert len(res_c4.plan.plan_hash) == 64
