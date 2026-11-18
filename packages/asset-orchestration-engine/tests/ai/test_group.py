"""
Tests for Squad & Group Dynamics System (UAF-81.57 Sections 101-104, 226).
"""

import pytest
from uaf.universal_ai import (
    GroupRole,
    SquadDefinition,
    FormationType,
)


def test_group_role_enum():
    roles = {r.value for r in GroupRole}
    expected = {
        "LEADER",
        "FOLLOWER",
        "SCOUT",
        "SUPPORT",
        "ATTACKER",
        "DEFENDER",
        "MEDIC",
        "CIVILIAN",
        "CUSTOM",
    }
    assert roles == expected


def test_squad_definition():
    squad = SquadDefinition(
        squad_id="SQUAD_BRAVO",
        leader_id="AGENT_LEAD",
        member_ids=["AGENT_M1", "AGENT_M2"],
        formation=FormationType.WEDGE,
    )
    assert squad.squad_id == "SQUAD_BRAVO"
    assert squad.leader_id == "AGENT_LEAD"
    assert len(squad.member_ids) == 2
    assert squad.formation == FormationType.WEDGE
    assert squad.shared_target is None


def test_squad_member_addition_removal():
    squad = SquadDefinition(squad_id="SQ1", leader_id="L1")
    assert len(squad.member_ids) == 0

    squad.member_ids.append("M1")
    squad.member_ids.append("M2")
    assert len(squad.member_ids) == 2

    squad.member_ids.remove("M1")
    assert squad.member_ids == ["M2"]


def test_squad_shared_target():
    squad = SquadDefinition(squad_id="SQ_ASSAULT", leader_id="L1", member_ids=["M1", "M2"])
    assert squad.shared_target is None

    squad.shared_target = "ENEMY_BOSS"
    assert squad.shared_target == "ENEMY_BOSS"


def test_squad_leader_succession():
    squad = SquadDefinition(squad_id="SQ_PATROL", leader_id="L1", member_ids=["M1", "M2", "M3"])

    # Simulate leader killed
    dead_leader = squad.leader_id
    if dead_leader == "L1" and squad.member_ids:
        squad.leader_id = squad.member_ids.pop(0)

    assert squad.leader_id == "M1"
    assert squad.member_ids == ["M2", "M3"]


def test_squad_formation_assignment():
    squad = SquadDefinition(squad_id="SQ_DEF", leader_id="L1")
    assert squad.formation == FormationType.WEDGE

    squad.formation = FormationType.LINE
    assert squad.formation == FormationType.LINE

    squad.formation = FormationType.COLUMN
    assert squad.formation == FormationType.COLUMN


def test_squad_all_members_count():
    squad = SquadDefinition(squad_id="SQ_COUNT", leader_id="LEAD", member_ids=["M1", "M2", "M3"])
    all_members = [squad.leader_id] + squad.member_ids
    assert len(all_members) == 4
