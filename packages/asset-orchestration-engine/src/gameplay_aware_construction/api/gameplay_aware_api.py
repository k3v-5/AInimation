from typing import Dict, Any, List, Optional, Tuple, Set
from ..core.gameplay_types import (
    ActorType, InteractionType, CollisionLayer, CollisionPurpose,
    SurfaceWalkability, TraversalType, GameplayTag, GameplaySeverity
)
from ..core.gameplay_schema import (
    ActorProfile, InteractionPoint, CollisionProfile, SpawnPoint,
    StairDefinition, DoorGameplayDefinition, GameplayContract,
    GameplayValidationReport, GameplaySpecification
)
from ..validation.scale_validator import GameplayScaleValidator
from ..validation.navigation_validator import GameplayNavigationValidator, GameplayTraversalValidator
from ..validation.interaction_validator import GameplayInteractionValidator, GameplaySpawnValidator
from ..agent.gameplay_test_agent import GameplayTestAgent
from ..impact.parameter_impact_graph import ParameterImpactGraph

class GameplayAwareAPI:
    """
    Gameplay-Aware Procedural Construction API (AOE v29)
    
    Regla Fundamental:
    VISUAL QUALITY + TECHNICAL QUALITY + GAMEPLAY VALIDITY = ACCEPTABLE ASSET.
    NINGÚN ASSET SE CONSIDERA VÁLIDO SI PRESENTA FALLOS CRÍTICOS DE JUGABILIDAD
    (SPAWN INVÁLIDO, PUERTA INACCESIBLE, ESCALERA INTRANSITABLE, OBJETIVO INALCANZABLE).
    """
    def __init__(self, primary_actor: Optional[ActorProfile] = None):
        self.primary_actor = primary_actor or ActorProfile()
        self.test_agent = GameplayTestAgent(self.primary_actor)

    def validate_asset_gameplay(
        self,
        asset_id: str,
        door: Optional[DoorGameplayDefinition] = None,
        stair: Optional[StairDefinition] = None,
        spawn: Optional[SpawnPoint] = None,
        interaction: Optional[InteractionPoint] = None,
        nav_graph: Optional[Dict[str, List[str]]] = None,
        start_node: str = "SPAWN",
        goal_node: Optional[str] = None,
        blocked_nodes: Optional[Set[str]] = None
    ) -> GameplayValidationReport:
        critical_errors: List[str] = []
        warnings: List[str] = []

        scale_status = GameplaySeverity.PASS
        collision_status = GameplaySeverity.PASS
        navigation_status = GameplaySeverity.PASS
        interaction_status = GameplaySeverity.PASS
        traversal_status = GameplaySeverity.PASS
        spawn_status = GameplaySeverity.PASS

        # 1. Validar escala de puerta y altura
        if door:
            door_issues = GameplayScaleValidator.validate_door_and_clearance(door, self.primary_actor)
            for sev, msg in door_issues:
                if sev == GameplaySeverity.CRITICAL:
                    scale_status = GameplaySeverity.CRITICAL
                    critical_errors.append(msg)
                else:
                    warnings.append(msg)

        # 2. Validar escaleras
        if stair:
            stair_issues = GameplayTraversalValidator.validate_stairs(stair, self.primary_actor)
            for sev, msg in stair_issues:
                if sev == GameplaySeverity.CRITICAL:
                    traversal_status = GameplaySeverity.CRITICAL
                    critical_errors.append(msg)
                else:
                    warnings.append(msg)

        # 3. Validar punto de spawn
        if spawn:
            spawn_issues = GameplaySpawnValidator.validate_spawn_point(spawn)
            for sev, msg in spawn_issues:
                if sev == GameplaySeverity.CRITICAL:
                    spawn_status = GameplaySeverity.CRITICAL
                    critical_errors.append(msg)
                else:
                    warnings.append(msg)

        # 4. Validar punto de interacción
        if interaction:
            inter_issues = GameplayInteractionValidator.validate_interaction_point(interaction, self.primary_actor)
            for sev, msg in inter_issues:
                if sev == GameplaySeverity.CRITICAL:
                    interaction_status = GameplaySeverity.CRITICAL
                    critical_errors.append(msg)
                else:
                    warnings.append(msg)

        # 5. Validar conectividad de navegación
        if nav_graph and goal_node:
            ok_nav, nav_logs = GameplayNavigationValidator.validate_connectivity(
                start_node, goal_node, nav_graph, blocked_nodes
            )
            if not ok_nav:
                navigation_status = GameplaySeverity.CRITICAL
                critical_errors.append(nav_logs[0])

        # Puntuación Gameplay
        score = 1.00
        if critical_errors:
            score -= (0.25 * len(critical_errors))
        if warnings:
            score -= (0.05 * len(warnings))
        final_score = max(0.10, round(score, 2))

        is_valid = len(critical_errors) == 0 and final_score >= 0.85

        return GameplayValidationReport(
            asset_id=asset_id,
            scale_status=scale_status,
            collision_status=collision_status,
            navigation_status=navigation_status,
            interaction_status=interaction_status,
            traversal_status=traversal_status,
            spawn_status=spawn_status,
            critical_errors=critical_errors,
            warnings=warnings,
            gameplay_score=final_score,
            is_valid=is_valid
        )

    def compute_combined_quality_score(
        self,
        visual_score: float,
        technical_score: float,
        gameplay_score: float,
        weights: Tuple[float, float, float] = (0.35, 0.25, 0.40)
    ) -> float:
        combined = (visual_score * weights[0]) + (technical_score * weights[1]) + (gameplay_score * weights[2])
        return round(combined, 3)

    def run_player_proxy_test(
        self,
        spawn: SpawnPoint,
        door: DoorGameplayDefinition,
        stair: Optional[StairDefinition] = None,
        interaction: Optional[InteractionPoint] = None,
        nav_graph: Optional[Dict[str, List[str]]] = None,
        goal_node: str = "OBJECTIVE",
        blocked_nodes: Optional[Set[str]] = None
    ) -> Tuple[bool, List[str], Optional[str]]:
        nav_g = nav_graph or {"SPAWN": ["DOOR"], "DOOR": [goal_node]}
        return self.test_agent.run_end_to_end_test(
            spawn=spawn,
            door=door,
            stair=stair,
            interaction=interaction,
            nav_graph=nav_g,
            goal_node=goal_node,
            blocked_nodes=blocked_nodes
        )

    def get_parameter_impact(self, parameter_name: str) -> List[str]:
        return ParameterImpactGraph.get_affected_systems(parameter_name)
