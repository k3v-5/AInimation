"""
Tests for Utility AI System (UAF-81.57 Sections 55-57, 226).
"""

import math
import pytest
from uaf.universal_ai import (
    UtilityCurveType,
    UtilityConsideration,
    UtilityAction,
    UniversalAIFabricator,
)


def test_utility_curve_types_enum():
    types = {t.value for t in UtilityCurveType}
    expected = {"LINEAR", "QUADRATIC", "EXPONENTIAL", "LOGISTIC", "CUSTOM"}
    assert types == expected


def test_utility_linear_curve():
    c = UtilityConsideration(name="hunger", curve_type=UtilityCurveType.LINEAR, weight=1.0)
    assert c.evaluate(0.0) == 0.0
    assert c.evaluate(0.5) == 0.5
    assert c.evaluate(1.0) == 1.0

    # Weight test
    c2 = UtilityConsideration(name="hunger", curve_type=UtilityCurveType.LINEAR, weight=2.0)
    assert c2.evaluate(0.5) == 1.0


def test_utility_quadratic_curve():
    c = UtilityConsideration(name="danger", curve_type=UtilityCurveType.QUADRATIC, weight=1.0)
    assert c.evaluate(0.0) == 0.0
    assert c.evaluate(0.5) == 0.25
    assert c.evaluate(1.0) == 1.0


def test_utility_exponential_curve():
    c = UtilityConsideration(name="threat", curve_type=UtilityCurveType.EXPONENTIAL, weight=1.0)
    # val = 0.0 -> exp(0)/e = 1/e ~ 0.367879
    assert round(c.evaluate(0.0), 3) == round(1.0 / math.e, 3)
    # val = 1.0 -> exp(1)/e = 1.0
    assert round(c.evaluate(1.0), 3) == 1.0


def test_utility_logistic_curve():
    c = UtilityConsideration(name="fatigue", curve_type=UtilityCurveType.LOGISTIC, weight=1.0)
    # val = 0.5 -> 1 / (1 + exp(0)) = 0.5
    assert round(c.evaluate(0.5), 3) == 0.5
    # val = 1.0 -> close to 1.0
    assert c.evaluate(1.0) > 0.99
    # val = 0.0 -> close to 0.0
    assert c.evaluate(0.0) < 0.01


def test_utility_action_combined_score():
    c1 = UtilityConsideration(name="health", curve_type=UtilityCurveType.LINEAR, weight=1.0)
    c2 = UtilityConsideration(name="ammo", curve_type=UtilityCurveType.LINEAR, weight=1.0)
    action = UtilityAction(
        action_id="ATTACK",
        considerations=[c1, c2],
        weight=1.0,
    )
    # Both 0.5 -> 0.5 * 0.5 = 0.25
    inputs = {"health": 0.5, "ammo": 0.5}
    assert action.calculate_utility(inputs) == 0.25


def test_utility_evaluate_highest_action():
    c_heal = UtilityConsideration(name="injury", curve_type=UtilityCurveType.LINEAR)
    c_patrol = UtilityConsideration(name="boredom", curve_type=UtilityCurveType.LINEAR)

    act_heal = UtilityAction("HEAL", considerations=[c_heal], weight=2.0)
    act_patrol = UtilityAction("PATROL", considerations=[c_patrol], weight=1.0)

    # When injury is high (0.9), HEAL utility = 0.9 * 2.0 = 1.8; PATROL utility = 0.5 * 1.0 = 0.5
    inputs = {"injury": 0.9, "boredom": 0.5}
    best = UniversalAIFabricator.evaluate_utility([act_heal, act_patrol], inputs)
    assert best.action_id == "HEAL"


def test_utility_evaluate_empty_raises():
    with pytest.raises(ValueError):
        UniversalAIFabricator.evaluate_utility([], {})
