"""
Tests for Social & Faction Dynamics System (UAF-81.57 Sections 90-95, 226).
"""

import pytest
from uaf.universal_ai import (
    FactionType,
    Relationship,
    FactionDefinition,
)


def test_faction_type_enum():
    types = {f.value for f in FactionType}
    expected = {"ALLY", "FRIENDLY", "NEUTRAL", "SUSPICIOUS", "HOSTILE"}
    assert types == expected


def test_relationship_creation():
    rel = Relationship(source="NPC_ALICE", target="NPC_BOB")
    assert rel.source == "NPC_ALICE"
    assert rel.target == "NPC_BOB"
    assert rel.affinity == 0.5
    assert rel.trust == 0.5
    assert rel.fear == 0.0
    assert rel.respect == 0.5
    assert rel.familiarity == 0.1
    assert rel.faction_relation == FactionType.NEUTRAL


def test_faction_definition():
    fac = FactionDefinition(
        faction_id="GUILD_THIEVES",
        name="Thieves Guild",
        default_relation=FactionType.SUSPICIOUS,
        relationships={"TOWN_GUARD": FactionType.HOSTILE, "SMUGGLERS": FactionType.FRIENDLY},
    )
    assert fac.faction_id == "GUILD_THIEVES"
    assert fac.name == "Thieves Guild"
    assert fac.default_relation == FactionType.SUSPICIOUS
    assert fac.relationships["TOWN_GUARD"] == FactionType.HOSTILE
    assert fac.relationships["SMUGGLERS"] == FactionType.FRIENDLY


def test_faction_relationship_lookup():
    fac = FactionDefinition(
        faction_id="KINGDOM",
        name="Kingdom Guards",
        default_relation=FactionType.NEUTRAL,
        relationships={"BANDITS": FactionType.HOSTILE, "MERCHANTS": FactionType.FRIENDLY},
    )
    # Explicit relation
    assert fac.relationships.get("BANDITS", fac.default_relation) == FactionType.HOSTILE
    assert fac.relationships.get("MERCHANTS", fac.default_relation) == FactionType.FRIENDLY
    # Fallback to default
    assert fac.relationships.get("NOMADS", fac.default_relation) == FactionType.NEUTRAL


def test_social_affinity_evolution():
    rel = Relationship(source="AGENT_1", target="AGENT_2", affinity=0.5, trust=0.5)

    # Positive event (gift or help)
    rel.affinity = min(1.0, rel.affinity + 0.2)
    rel.trust = min(1.0, rel.trust + 0.15)
    rel.familiarity = min(1.0, rel.familiarity + 0.1)

    assert round(rel.affinity, 2) == 0.70
    assert round(rel.trust, 2) == 0.65
    assert round(rel.familiarity, 2) == 0.20


def test_hostile_interaction():
    rel = Relationship(source="AGENT_1", target="AGENT_2", affinity=0.5, trust=0.5, fear=0.0)

    # Threat or attack event
    rel.affinity = max(0.0, rel.affinity - 0.4)
    rel.trust = max(0.0, rel.trust - 0.4)
    rel.fear = min(1.0, rel.fear + 0.6)
    rel.faction_relation = FactionType.HOSTILE

    assert round(rel.affinity, 2) == 0.10
    assert round(rel.trust, 2) == 0.10
    assert round(rel.fear, 2) == 0.60
    assert rel.faction_relation == FactionType.HOSTILE
