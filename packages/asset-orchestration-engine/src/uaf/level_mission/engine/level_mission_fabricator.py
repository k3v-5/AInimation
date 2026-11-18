"""
LevelMissionFabricationPlatform manufactures canonical Golden Levels matching Section 142.
UAF-81.41 Sections 142, 143.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    PlayableLevelSpecification,
    MissionNodeType41,
    MissionFlowMetrics41,
)


class LevelMissionFabricationPlatform:
    """
    Synthesizes complete, production-grade playable levels, mission flows, and gameplay packages for Unreal Engine.
    """

    @classmethod
    def build_golden_linear_mission(cls, level_id: str = "Level_Gold_Linear") -> Tuple[PlayableLevelSpecification, str, str]:
        """1. GOLDEN_LINEAR_MISSION (Section 142: 3 sequential objectives, 2 checkpoints)."""
        metrics = MissionFlowMetrics41(primary_objective_count=3, encounter_count=2, checkpoint_count=2, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_Forest", MissionNodeType41.OBJECTIVE, metrics, ai_spaces_count=3)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"

    @classmethod
    def build_golden_open_exploration(cls, level_id: str = "Level_Gold_OpenExploration") -> Tuple[PlayableLevelSpecification, str, str]:
        """2. GOLDEN_OPEN_EXPLORATION (Section 142: exploration hubs, optional objectives)."""
        metrics = MissionFlowMetrics41(primary_objective_count=2, encounter_count=3, checkpoint_count=3, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_Desert", MissionNodeType41.TRAVEL, metrics, ai_spaces_count=4)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"

    @classmethod
    def build_golden_combat_mission(cls, level_id: str = "Level_Gold_Combat") -> Tuple[PlayableLevelSpecification, str, str]:
        """3. GOLDEN_COMBAT_MISSION (Section 142: heavy enemy encounters, combat arenas)."""
        metrics = MissionFlowMetrics41(primary_objective_count=4, encounter_count=5, checkpoint_count=4, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_Combat", MissionNodeType41.COMBAT, metrics, ai_spaces_count=5)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"

    @classmethod
    def build_golden_stealth_mission(cls, level_id: str = "Level_Gold_Stealth") -> Tuple[PlayableLevelSpecification, str, str]:
        """4. GOLDEN_STEALTH_MISSION (Section 142: patrol paths, alert zones, infiltration)."""
        metrics = MissionFlowMetrics41(primary_objective_count=2, encounter_count=2, checkpoint_count=2, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_Industrial", MissionNodeType41.STEALTH, metrics, ai_spaces_count=3)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"

    @classmethod
    def build_golden_boss_mission(cls, level_id: str = "Level_Gold_Boss") -> Tuple[PlayableLevelSpecification, str, str]:
        """5. GOLDEN_BOSS_MISSION (Section 142: multi-phase boss arena, pre-boss checkpoint)."""
        metrics = MissionFlowMetrics41(primary_objective_count=1, encounter_count=1, checkpoint_count=2, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_SciFi", MissionNodeType41.BOSS, metrics, ai_spaces_count=2)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"

    @classmethod
    def build_golden_branching_mission(cls, level_id: str = "Level_Gold_Branching") -> Tuple[PlayableLevelSpecification, str, str]:
        """6. GOLDEN_BRANCHING_MISSION (Section 142: alternate routes, dual objectives)."""
        metrics = MissionFlowMetrics41(primary_objective_count=3, encounter_count=3, checkpoint_count=3, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_Urban", MissionNodeType41.OBJECTIVE, metrics, ai_spaces_count=4)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"

    @classmethod
    def build_golden_defense_mission(cls, level_id: str = "Level_Gold_Defense") -> Tuple[PlayableLevelSpecification, str, str]:
        """7. GOLDEN_DEFENSE_MISSION (Section 142: survive wave triggers, fortified perimeter)."""
        metrics = MissionFlowMetrics41(primary_objective_count=2, encounter_count=4, checkpoint_count=2, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_Combat", MissionNodeType41.DEFENSE, metrics, ai_spaces_count=3)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"

    @classmethod
    def build_golden_extraction_mission(cls, level_id: str = "Level_Gold_Extraction") -> Tuple[PlayableLevelSpecification, str, str]:
        """8. GOLDEN_EXTRACTION_MISSION (Section 142: timed escape, high urgency extraction trigger)."""
        metrics = MissionFlowMetrics41(primary_objective_count=2, encounter_count=3, checkpoint_count=2, has_valid_player_start=True, has_extraction_or_end=True)
        spec = PlayableLevelSpecification(level_id, "World_Gold_Mountain", MissionNodeType41.EXTRACTION, metrics, ai_spaces_count=3)
        return spec, f"/Game/Missions/Graphs/MG_{level_id}", f"/Game/Missions/Packages/GP_{level_id}"
