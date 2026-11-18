"""
UAF-81.92: Dynamic Faction Reputation & Diplomatic Ripple Effects.
Tracks pairwise faction dispositions [-100.0, +100.0] and propagates alliance ripple cascades
when crimes or combat incidents occur.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from pydantic import BaseModel, Field

from uaf.ai.core.contracts import FactionId, DispositionType


class FactionReputationMatrix(BaseModel):
    """
    Symmetric and asymmetric diplomatic disposition graph between factions.
    Scores range from -100.0 (Kill on Sight / War) to +100.0 (Staunch Ally).
    """
    dispositions: Dict[Tuple[str, str], float] = Field(default_factory=dict)

    @classmethod
    def create_default_matrix(cls) -> FactionReputationMatrix:
        """Initializes standard baseline relationships between core factions."""
        matrix = cls()
        factions = list(FactionId)

        # Baseline: self is 100.0, others default to 0.0 (Neutral)
        for fa in factions:
            for fb in factions:
                if fa == fb:
                    matrix.set_disposition(fa, fb, 100.0)
                else:
                    matrix.set_disposition(fa, fb, 0.0)

        # Feral Xenos are hostile to everyone
        for f in factions:
            if f != FactionId.FERAL_XENOS:
                matrix.set_disposition(FactionId.FERAL_XENOS, f, -100.0)
                matrix.set_disposition(f, FactionId.FERAL_XENOS, -100.0)

        # Colonial Security vs Raiders: Hostile
        matrix.set_disposition(FactionId.COLONIAL_SECURITY, FactionId.RENEGADE_RAIDERS, -80.0)
        matrix.set_disposition(FactionId.RENEGADE_RAIDERS, FactionId.COLONIAL_SECURITY, -80.0)

        # Military Syndicate and Colonial Security: Strong Alliance
        matrix.set_disposition(FactionId.MILITARY_SYNDICATE, FactionId.COLONIAL_SECURITY, 65.0)
        matrix.set_disposition(FactionId.COLONIAL_SECURITY, FactionId.MILITARY_SYNDICATE, 65.0)

        # Player starting disposition: Friendly with Colonial Security, Neutral with Syndicate, Hostile with Raiders
        matrix.set_disposition(FactionId.PLAYER, FactionId.COLONIAL_SECURITY, 40.0)
        matrix.set_disposition(FactionId.COLONIAL_SECURITY, FactionId.PLAYER, 40.0)

        matrix.set_disposition(FactionId.PLAYER, FactionId.RENEGADE_RAIDERS, -70.0)
        matrix.set_disposition(FactionId.RENEGADE_RAIDERS, FactionId.PLAYER, -70.0)

        return matrix

    def get_disposition(self, faction_a: str, faction_b: str) -> float:
        """Retrieves raw disposition score in [-100.0, +100.0]."""
        if faction_a == faction_b:
            return 100.0
        return self.dispositions.get((faction_a, faction_b), 0.0)

    def set_disposition(self, faction_a: str, faction_b: str, value: float) -> None:
        """Sets clamped disposition value in [-100.0, +100.0]."""
        self.dispositions[(faction_a, faction_b)] = max(-100.0, min(100.0, round(value, 2)))

    def get_relationship_type(self, faction_a: str, faction_b: str) -> DispositionType:
        """Evaluates whether the disposition constitutes HOSTILE, NEUTRAL, or ALLIED status."""
        score = self.get_disposition(faction_a, faction_b)
        if score < -30.0:
            return DispositionType.HOSTILE
        if score > 30.0:
            return DispositionType.ALLIED
        return DispositionType.NEUTRAL

    def modify_disposition(
        self,
        actor_faction: str,
        target_faction: str,
        delta: float,
        propagate_ripple: bool = True,
    ) -> List[Tuple[str, str, float]]:
        """
        Adjusts disposition of target_faction towards actor_faction by delta.
        If propagate_ripple is True, cascades proportional diplomatic reactions
        to target_faction's allies.
        Returns list of (evaluating_faction, actor_faction, new_disposition).
        """
        changes: List[Tuple[str, str, float]] = []

        # Direct change
        curr = self.get_disposition(target_faction, actor_faction)
        new_val = max(-100.0, min(100.0, curr + delta))
        self.set_disposition(target_faction, actor_faction, new_val)
        changes.append((target_faction, actor_faction, new_val))

        if propagate_ripple and delta != 0.0:
            # Find all factions allied with target_faction
            for (f_other, f_targ), ally_score in list(self.dispositions.items()):
                if f_targ == target_faction and f_other != actor_faction and f_other != target_faction:
                    if ally_score > 20.0:  # Is ally or positive friend
                        # Proportional ripple: ally reacts with fraction of their friendship strength
                        ripple_delta = delta * (ally_score / 100.0)
                        other_curr = self.get_disposition(f_other, actor_faction)
                        other_new = max(-100.0, min(100.0, other_curr + ripple_delta))
                        self.set_disposition(f_other, actor_faction, other_new)
                        changes.append((f_other, actor_faction, other_new))

        return changes
