from typing import Dict, Any, Tuple, List
from ..core.parametric_schema import ParametricAssetDefinition, ParameterChange
from ..core.parameter_graph import ParameterDependencyGraph
from .constraint_solver import ParameterConstraintSolver

class ParameterTransactionManager:
    @staticmethod
    def apply_transaction(
        definition: ParametricAssetDefinition,
        current_parameters: Dict[str, Any],
        changes: List[ParameterChange]
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        backup = dict(current_parameters)
        working = dict(current_parameters)

        for chg in changes:
            if chg.operation == "SET":
                working[chg.parameter_name] = chg.new_value
            elif chg.operation == "INCREASE_PERCENT":
                old_v = working.get(chg.parameter_name, 1.0)
                working[chg.parameter_name] = round(old_v * (1.0 + chg.new_value), 4)
            elif chg.operation == "DECREASE_PERCENT":
                old_v = working.get(chg.parameter_name, 1.0)
                working[chg.parameter_name] = round(old_v * (1.0 - chg.new_value), 4)

        # Recalcular dependencias
        resolved = ParameterDependencyGraph.resolve_parameters(definition, working)

        # Validar restricciones
        is_valid, errors = ParameterConstraintSolver.validate_constraints(definition, resolved)
        if not is_valid:
            # Rollback total
            return False, backup, [f"TRANSACTION_ROLLED_BACK: {e}" for e in errors]

        return True, resolved, ["Transaction committed successfully."]
