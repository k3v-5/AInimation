from typing import Dict, Any, List
from .parametric_schema import ParametricAssetDefinition
from ..solver.formula_engine import ParameterFormulaEngine

class ParameterDependencyGraph:
    @staticmethod
    def resolve_parameters(
        definition: ParametricAssetDefinition,
        explicit_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        resolved = {}

        # 1. Establecer defaults
        for p_name, p_def in definition.parameters.items():
            resolved[p_name] = p_def.default_value

        # 2. Aplicar explícitos
        for p_name, val in explicit_parameters.items():
            if p_name in definition.parameters:
                resolved[p_name] = val

        # 3. Calcular parámetros derivados automáticamente
        for p_name, p_def in definition.parameters.items():
            if p_def.is_derived and p_def.formula:
                resolved[p_name] = ParameterFormulaEngine.evaluate(p_def.formula, resolved)

        # Reglas estándar de derivación para casas y estructuras
        if "width" in resolved:
            w = resolved["width"]
            resolved["roof_width"] = round(w + 0.40, 4)
            resolved["foundation_width"] = round(w + 0.20, 4)
            win_cnt = resolved.get("window_count", 4)
            resolved["window_spacing"] = round((w - 1.0) / max(1, win_cnt - 1), 4)

        if "height" in resolved:
            h = resolved["height"]
            if "roof_height" not in explicit_parameters:
                resolved["roof_height"] = round(h * 0.35, 4)
            if "wall_height" not in explicit_parameters:
                resolved["wall_height"] = round(h * 0.65, 4)

        return resolved
