"""
Tests for Formations System (UAF-81.57 Sections 86-89, 226).
"""

import math
import pytest
from uaf.universal_ai import (
    FormationType,
    FormationMember,
    FormationDefinition,
    UniversalAIFabricator,
)


def test_formation_types_enum():
    types = {t.value for t in FormationType}
    expected = {"LINE", "COLUMN", "WEDGE", "CIRCLE", "SQUARE", "CUSTOM"}
    assert types == expected


def test_formation_member_and_definition():
    m1 = FormationMember(agent_id="SOLDIER_1", slot_index=0, offset=(-100.0, 0.0, 0.0), role="LEADER")
    m2 = FormationMember(agent_id="SOLDIER_2", slot_index=1, offset=(100.0, 0.0, 0.0), role="RIFLEMAN")
    f_def = FormationDefinition(
        formation_id="FORM_ALPHA",
        formation_type=FormationType.LINE,
        spacing=200.0,
        members=[m1, m2],
    )
    assert f_def.formation_id == "FORM_ALPHA"
    assert f_def.formation_type == FormationType.LINE
    assert len(f_def.members) == 2
    assert f_def.members[0].role == "LEADER"


def test_formation_slots_line():
    slots = UniversalAIFabricator.compute_formation_slots(FormationType.LINE, count=3, spacing=100.0)
    assert len(slots) == 3
    # Centered: x = -100, 0, 100
    assert round(slots[0][0], 2) == -100.0
    assert round(slots[1][0], 2) == 0.0
    assert round(slots[2][0], 2) == 100.0
    assert all(s[1] == 0.0 for s in slots)


def test_formation_slots_column():
    slots = UniversalAIFabricator.compute_formation_slots(FormationType.COLUMN, count=3, spacing=150.0)
    assert len(slots) == 3
    # Centered along Y: y = -150, 0, 150
    assert round(slots[0][1], 2) == -150.0
    assert round(slots[1][1], 2) == 0.0
    assert round(slots[2][1], 2) == 150.0
    assert all(s[0] == 0.0 for s in slots)


def test_formation_slots_wedge():
    slots = UniversalAIFabricator.compute_formation_slots(FormationType.WEDGE, count=3, spacing=100.0)
    assert len(slots) == 3
    # Rank 0 is apex, ranks 1 and 2 spread in X and step back in Y
    assert slots[0][1] <= 0.0
    assert slots[1][1] <= 0.0
    assert slots[2][1] <= 0.0


def test_formation_slots_circle():
    count = 8
    slots = UniversalAIFabricator.compute_formation_slots(FormationType.CIRCLE, count=count, spacing=100.0)
    assert len(slots) == count
    radius = 100.0 * count / (2 * math.pi)
    # Check that each slot is approximately at distance `radius` from origin
    for slot in slots:
        d = math.sqrt(slot[0]**2 + slot[1]**2)
        assert round(d, 1) == round(radius, 1)


def test_formation_slot_count_zero():
    slots = UniversalAIFabricator.compute_formation_slots(FormationType.LINE, count=0)
    assert len(slots) == 0
