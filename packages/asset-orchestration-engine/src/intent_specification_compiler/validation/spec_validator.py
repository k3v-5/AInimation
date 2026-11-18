from typing import List, Tuple
from ..core.spec_types import SpecStatus, ApprovalState
from ..core.spec_schema import AssetSpec

class SpecificationValidator:
    @staticmethod
    def validate_spec(spec: AssetSpec) -> Tuple[bool, List[str]]:
        conflicts = []

        # 1. Validar conflicto de puerta y paso de jugador
        if spec.door.player_passable and spec.door.width_m < 0.80:
            conflicts.append(
                f"SPEC_CONFLICT: Door width ({spec.door.width_m:.2f}m) is below minimum (0.80m) for 'player_passable = true'."
            )

        # 2. Validar escaleras y requisitos de planta
        if spec.stairs.required and spec.stairs.destination == "SECOND_FLOOR" and spec.visual.scale == "TINY":
            conflicts.append("SPEC_CONFLICT: Scale 'TINY' cannot accommodate a two-story staircase.")

        # 3. Validar consistencia de estilo
        if "FANTASY" in spec.style.forbidden_styles and "FANTASY" in spec.style.architecture:
            conflicts.append("SPEC_CONFLICT: Style contains 'FANTASY' while forbidden_styles excludes it.")

        is_valid = len(conflicts) == 0
        if is_valid:
            spec.status = SpecStatus.VALIDATED
            spec.approval = ApprovalState.APPROVED
        else:
            spec.approval = ApprovalState.REJECTED

        return is_valid, conflicts
