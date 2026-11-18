from enum import Enum
from typing import Tuple, Dict, Any, Optional
from ..scene.actor_registry import UnrealActor

class SpatialRelation(str, Enum):
    ON_TOP_OF = "ON_TOP_OF"
    IN_FRONT_OF = "IN_FRONT_OF"
    BEHIND = "BEHIND"
    LEFT_OF = "LEFT_OF"
    RIGHT_OF = "RIGHT_OF"
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    NEAR = "NEAR"
    ATTACHED_TO = "ATTACHED_TO"
    CENTERED_ON = "CENTERED_ON"

class SpatialSolver:
    @staticmethod
    def solve_position(
        target_actor: UnrealActor,
        relation: SpatialRelation,
        reference_actor: UnrealActor,
        offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    ) -> Tuple[float, float, float]:
        ref_loc = reference_actor.transform.location
        ref_w, ref_d, ref_h = reference_actor.dimensions_cm
        tar_w, tar_d, tar_h = target_actor.dimensions_cm

        if relation == SpatialRelation.ON_TOP_OF:
            # Colocar exactamente encima de la superficie superior de la referencia
            new_x = ref_loc[0] + offset[0]
            new_y = ref_loc[1] + offset[1]
            new_z = ref_loc[2] + ref_h + offset[2]
            return (round(new_x, 2), round(new_y, 2), round(new_z, 2))

        elif relation == SpatialRelation.IN_FRONT_OF:
            new_x = ref_loc[0] + (ref_w / 2.0) + (tar_w / 2.0) + 10.0 + offset[0]
            new_y = ref_loc[1] + offset[1]
            new_z = ref_loc[2] + offset[2]
            return (round(new_x, 2), round(new_y, 2), round(new_z, 2))

        elif relation == SpatialRelation.ABOVE:
            new_x = ref_loc[0] + offset[0]
            new_y = ref_loc[1] + offset[1]
            new_z = ref_loc[2] + ref_h + 50.0 + offset[2]
            return (round(new_x, 2), round(new_y, 2), round(new_z, 2))

        elif relation == SpatialRelation.CENTERED_ON:
            new_x = ref_loc[0] + offset[0]
            new_y = ref_loc[1] + offset[1]
            new_z = ref_loc[2] + offset[2]
            return (round(new_x, 2), round(new_y, 2), round(new_z, 2))

        else: # Fallback / NEAR
            new_x = ref_loc[0] + (ref_w / 2.0) + 20.0 + offset[0]
            new_y = ref_loc[1] + offset[1]
            new_z = ref_loc[2] + offset[2]
            return (round(new_x, 2), round(new_y, 2), round(new_z, 2))
