"""
UAF-81.82: Utility-Based Target Selection and Team Relationships.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from ..models.definition import TeamRelation, Vec3, vec3_distance


class TeamRelationProvider:
    """Provides relational disposition (Friendly, Neutral, Hostile, Unknown) between teams."""

    def __init__(self):
        self._overrides: Dict[Tuple[str, str], TeamRelation] = {}

    def set_relation(self, team_a: str, team_b: str, relation: TeamRelation) -> None:
        self._overrides[(team_a, team_b)] = relation
        self._overrides[(team_b, team_a)] = relation

    def get_relation(self, team_a: str, team_b: str) -> TeamRelation:
        if team_a == team_b:
            return TeamRelation.FRIENDLY

        override = self._overrides.get((team_a, team_b))
        if override is not None:
            return override

        # Default rules
        if "neutral" in (team_a.lower(), team_b.lower()):
            return TeamRelation.NEUTRAL

        if (team_a.lower() == "player" and team_b.lower() == "enemy") or \
           (team_a.lower() == "enemy" and team_b.lower() == "player"):
            return TeamRelation.HOSTILE

        return TeamRelation.NEUTRAL


class TargetSelector:
    """
    Evaluates candidate targets using a pure mathematical utility function.
    Deterministic tie-breaking: (score DESC, entity_id ASC).
    """

    @staticmethod
    def calculate_score(
        observer_pos: Vec3,
        target_pos: Vec3,
        threat_level: float = 1.0,
        is_visible: bool = True,
        damage_received_from_target: float = 0.0,
        tactical_value: float = 0.0,
    ) -> float:
        """Compute utility score for engaging a target."""
        dist = vec3_distance(observer_pos, target_pos)
        dist_score = max(0.0, 50.0 - dist)
        vis_score = 30.0 if is_visible else 0.0
        dmg_score = damage_received_from_target * 1.5
        threat_score = threat_level * 20.0

        return threat_score + dist_score + vis_score + dmg_score + tactical_value

    @staticmethod
    def select_best_target(
        candidates: List[Tuple[str, float]],  # List of (entity_id, score)
    ) -> Optional[str]:
        """Select highest scoring candidate. Breaks ties strictly by entity_id ASC."""
        if not candidates:
            return None

        # Sort: score DESC, entity_id ASC
        sorted_cand = sorted(candidates, key=lambda item: (-item[1], item[0]))
        return sorted_cand[0][0]
