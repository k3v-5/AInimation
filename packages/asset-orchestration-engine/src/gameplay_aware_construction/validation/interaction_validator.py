from typing import List, Tuple
from ..core.gameplay_types import GameplaySeverity
from ..core.gameplay_schema import InteractionPoint, SpawnPoint, ActorProfile

class GameplayInteractionValidator:
    @staticmethod
    def validate_interaction_point(
        point: InteractionPoint,
        actor: ActorProfile
    ) -> List[Tuple[GameplaySeverity, str]]:
        issues = []
        if point.is_blocked:
            issues.append((
                GameplaySeverity.CRITICAL,
                f"INTERACTION_BLOCKED: Interaction point '{point.point_id}' ({point.interaction_type.value}) is blocked by solid collision."
            ))

        if point.required_clearance < actor.clearance * 0.90:
            issues.append((
                GameplaySeverity.HIGH,
                f"INTERACTION_CLEARANCE_TOO_SMALL: Clearance for '{point.point_id}' ({point.required_clearance:.2f}m) is less than required ({actor.clearance:.2f}m)."
            ))

        return issues

class GameplaySpawnValidator:
    @staticmethod
    def validate_spawn_point(
        spawn: SpawnPoint
    ) -> List[Tuple[GameplaySeverity, str]]:
        issues = []
        if spawn.is_inside_geometry:
            issues.append((
                GameplaySeverity.CRITICAL,
                f"SPAWN_INSIDE_GEOMETRY: Spawn point '{spawn.spawn_id}' is located inside solid geometry or collision."
            ))

        if not spawn.is_valid_ground:
            issues.append((
                GameplaySeverity.CRITICAL,
                f"SPAWN_INVALID_GROUND: Spawn point '{spawn.spawn_id}' is placed over void or non-walkable surface."
            ))

        return issues
