from typing import Tuple, Dict, Any, Optional
from ..core.governance_schema import ActionProposal, ActionScope
from ...intent_compiler.core.intent_schema import BuildSpecification

class ActionValidator:
    PARAMETER_LIMITS = {
        "roof_height": (0.10, 3.00),
        "blade_length": (0.30, 2.50),
        "scale": (0.10, 5.00),
        "width": (0.50, 20.0)
    }

    @classmethod
    def validate_proposal(
        cls,
        proposal: ActionProposal,
        spec: Optional[BuildSpecification] = None
    ) -> Tuple[bool, str]:
        # 1. Comprobar límites de parámetros
        for p_name, p_val in proposal.parameters.items():
            if p_name in cls.PARAMETER_LIMITS and isinstance(p_val, (int, float)):
                min_v, max_v = cls.PARAMETER_LIMITS[p_name]
                if p_val < min_v or p_val > max_v:
                    return False, f"PARAMETER_OUT_OF_RANGE: {p_name}={p_val} exceeds allowed range [{min_v}, {max_v}]."

        # 2. Comprobar escalada de alcance no autorizada
        if proposal.scope in [ActionScope.SCENE, ActionScope.PROJECT] and proposal.action_name == "modify_component":
            return False, "UNAUTHORIZED_SCOPE_ESCALATION: Cannot escalate component modification to entire SCENE scope."

        # 3. Comprobar protección de restricciones explícitas de BuildSpecification
        if spec and proposal.target_entity:
            # Si el usuario pidió exactamente 4m de ancho y la IA intenta cambiarlo a 5m sin propuesta de cambio
            if "width" in proposal.parameters and "length" in spec.requirements:
                exp_req = spec.requirements["length"]
                if exp_req.source == "USER_EXPLICIT" and abs(proposal.parameters["width"] - exp_req.value) > 0.01:
                    return False, f"REQUIREMENT_MUTATION_DENIED: Cannot mutate explicit user requirement ({exp_req.value}m) to {proposal.parameters['width']}m."

        return True, "Proposal valid."
