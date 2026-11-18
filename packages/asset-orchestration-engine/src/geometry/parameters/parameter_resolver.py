import re
from typing import Dict, Any, Optional

class ParameterResolver:
    @staticmethod
    def resolve_derived_parameters(
        target_component: str,
        current_parameters: Dict[str, Any],
        context_parameters: Dict[str, Dict[str, Any]],
        derived_rules: Dict[str, str] # e.g. "width": "blade.width * 3"
    ) -> Dict[str, Any]:
        """
        Calcula parámetros derivados a partir del contexto de otros componentes.
        """
        resolved = dict(current_parameters)
        for param_name, formula in derived_rules.items():
            # Buscar referencias tipo 'comp_id.param_name'
            matches = re.findall(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', formula)
            eval_scope = {}
            valid_formula = True
            for comp_name, p_name in matches:
                # Buscar en context_parameters
                found = False
                for full_cid, p_dict in context_parameters.items():
                    if full_cid.endswith(comp_name) or full_cid == comp_name:
                        val = p_dict.get(p_name)
                        if val is not None:
                            var_clean = f"{comp_name}_{p_name}"
                            formula = formula.replace(f"{comp_name}.{p_name}", var_clean)
                            eval_scope[var_clean] = float(val)
                            found = True
                            break
                if not found:
                    valid_formula = False
                    break

            if valid_formula:
                try:
                    # Evaluación segura matemática básica
                    calc_val = eval(formula, {"__builtins__": None}, eval_scope)
                    resolved[param_name] = round(float(calc_val), 6)
                except Exception:
                    pass

        return resolved
