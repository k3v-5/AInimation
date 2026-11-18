"""
Tests for Factions and Reputation System (UAF-81.58 Sections 176-185, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    FactionReputationTier,
    FactionReputation,
    GameplayState,
)


def test_faction_reputation_tier_enum():
    tiers = {t.value for t in FactionReputationTier}
    expected = {"HATED", "HOSTILE", "UNFRIENDLY", "NEUTRAL", "FRIENDLY", "HONORED", "EXALTED"}
    assert tiers == expected


def test_faction_reputation_neutral_default():
    rep = FactionReputation(faction_id="FACTION_GUILD")
    assert rep.faction_id == "FACTION_GUILD"
    assert rep.score == 0.0
    assert rep.tier == FactionReputationTier.NEUTRAL


def test_faction_reputation_negative_tiers():
    r_unfriendly = FactionReputation("f1", -50.0)
    assert r_unfriendly.tier == FactionReputationTier.UNFRIENDLY

    r_hostile = FactionReputation("f2", -300.0)
    assert r_hostile.tier == FactionReputationTier.HOSTILE

    r_hated = FactionReputation("f3", -750.0)
    assert r_hated.tier == FactionReputationTier.HATED


def test_faction_reputation_positive_tiers():
    r_friendly = FactionReputation("f1", 350.0)
    assert r_friendly.tier == FactionReputationTier.FRIENDLY

    r_honored = FactionReputation("f2", 650.0)
    assert r_honored.tier == FactionReputationTier.HONORED

    r_exalted = FactionReputation("f3", 950.0)
    assert r_exalted.tier == FactionReputationTier.EXALTED


def test_faction_reputation_boundary_values():
    assert FactionReputation("f", -500.0).tier == FactionReputationTier.HATED
    assert FactionReputation("f", -200.0).tier == FactionReputationTier.HOSTILE
    assert FactionReputation("f", -0.1).tier == FactionReputationTier.UNFRIENDLY
    assert FactionReputation("f", 0.0).tier == FactionReputationTier.NEUTRAL
    assert FactionReputation("f", 200.0).tier == FactionReputationTier.FRIENDLY
    assert FactionReputation("f", 500.0).tier == FactionReputationTier.HONORED
    assert FactionReputation("f", 800.0).tier == FactionReputationTier.EXALTED


def test_faction_reputation_dynamic_mutation():
    rep = FactionReputation("FACTION_BANDITS", 0.0)
    assert rep.tier == FactionReputationTier.NEUTRAL

    rep.score -= 250.0
    assert rep.tier == FactionReputationTier.HOSTILE

    rep.score += 700.0  # -250 + 700 = 450
    assert rep.tier == FactionReputationTier.FRIENDLY

    rep.score += 400.0  # 450 + 400 = 850
    assert rep.tier == FactionReputationTier.EXALTED


def test_faction_reputation_in_gameplay_state():
    state = GameplayState("SIM_FACTIONS")
    f_knights = FactionReputation("KNIGHTS", 550.0)
    f_thieves = FactionReputation("THIEVES", -400.0)
    state.factions[f_knights.faction_id] = f_knights
    state.factions[f_thieves.faction_id] = f_thieves

    assert len(state.factions) == 2
    assert state.factions["KNIGHTS"].tier == FactionReputationTier.HONORED
    assert state.factions["THIEVES"].tier == FactionReputationTier.HOSTILE
