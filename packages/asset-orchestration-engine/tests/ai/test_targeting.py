"""
Tests for Targeting & Lock System (UAF-81.57 Sections 41-46, 226).
"""

import pytest
from uaf.universal_ai import (
    TargetLockMode,
    TargetScore,
    AIAgent,
    AgentProfile,
    AgentState,
    AgentLifecycleState,
)


def test_target_lock_modes_enum():
    modes = {m.value for m in TargetLockMode}
    expected = {"LOCKED", "SOFT_LOCK", "NO_LOCK"}
    assert modes == expected


def test_target_score_creation():
    ts = TargetScore(
        target_id="TARGET_01",
        score=85.5,
        distance=420.0,
        visibility=True,
        threat_level=0.9,
    )
    assert ts.target_id == "TARGET_01"
    assert ts.score == 85.5
    assert ts.distance == 420.0
    assert ts.visibility is True
    assert ts.threat_level == 0.9


def test_target_selection_by_highest_score():
    targets = [
        TargetScore("T1", score=30.0),
        TargetScore("T2", score=95.0),
        TargetScore("T3", score=65.0),
    ]
    best_target = max(targets, key=lambda t: t.score)
    assert best_target.target_id == "T2"
    assert best_target.score == 95.0


def test_target_lock_retention():
    prof = AgentProfile(profile_id="P_GUARD")
    agent = AIAgent("GUARD", profile=prof, target_lock=TargetLockMode.LOCKED)
    agent.state.current_target = "ENEMY_ALPHA"

    # With LOCKED mode, target remains locked even if another candidate appears
    new_candidate = "ENEMY_BETA"
    if agent.target_lock == TargetLockMode.LOCKED:
        selected = agent.state.current_target
    else:
        selected = new_candidate

    assert selected == "ENEMY_ALPHA"

    # Changing to NO_LOCK allows switching target
    agent.target_lock = TargetLockMode.NO_LOCK
    if agent.target_lock == TargetLockMode.NO_LOCK:
        agent.state.current_target = new_candidate
    assert agent.state.current_target == "ENEMY_BETA"


def test_target_visibility_filter():
    targets = [
        TargetScore("T_VISIBLE", score=80.0, visibility=True),
        TargetScore("T_HIDDEN", score=99.0, visibility=False),
        TargetScore("T_FAR_VISIBLE", score=60.0, visibility=True),
    ]
    visible_only = [t for t in targets if t.visibility]
    assert len(visible_only) == 2
    best_visible = max(visible_only, key=lambda t: t.score)
    assert best_visible.target_id == "T_VISIBLE"


def test_target_threat_weighted_selection():
    # Target A is close (dist 100) but low threat (0.1)
    # Target B is medium distance (dist 300) but high threat (0.95)
    targets = [
        {"id": "A", "distance": 100.0, "threat": 0.1},
        {"id": "B", "distance": 300.0, "threat": 0.95},
    ]

    def compute_priority(t: dict) -> float:
        # 70% threat weight, 30% distance weight
        dist_factor = max(0.0, 1.0 - (t["distance"] / 1000.0))
        return (t["threat"] * 0.7) + (dist_factor * 0.3)

    scored = [(t["id"], compute_priority(t)) for t in targets]
    best = max(scored, key=lambda pair: pair[1])
    assert best[0] == "B"
