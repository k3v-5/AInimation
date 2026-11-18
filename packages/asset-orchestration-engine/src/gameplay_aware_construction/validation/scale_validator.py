from typing import List, Tuple
from ..core.gameplay_types import GameplaySeverity
from ..core.gameplay_schema import ActorProfile, DoorGameplayDefinition

class GameplayScaleValidator:
    @staticmethod
    def validate_door_and_clearance(
        door: DoorGameplayDefinition,
        actor: ActorProfile
    ) -> List[Tuple[GameplaySeverity, str]]:
        issues = []
        # Validar ancho de puerta
        if door.width < actor.clearance:
            issues.append((
                GameplaySeverity.CRITICAL,
                f"DOOR_TOO_NARROW: Door width ({door.width:.2f}m) is less than required actor clearance ({actor.clearance:.2f}m)."
            ))

        # Validar altura de puerta
        if door.height < actor.height + 0.15:
            issues.append((
                GameplaySeverity.HIGH,
                f"DOOR_TOO_LOW: Door height ({door.height:.2f}m) is less than required actor height + safety ({actor.height + 0.15:.2f}m)."
            ))

        return issues
