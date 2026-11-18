from typing import Dict, Any
from ..templates.base_template import IAssetTemplate
from ...spec_compiler.core.asset_spec import AssetSpec

class ParameterResolver:
    @staticmethod
    def resolve_parameters(spec: AssetSpec, template: IAssetTemplate) -> Dict[str, Any]:
        param_defs = template.get_parameter_definitions()
        resolved: Dict[str, Any] = {}

        # 1. Cargar defaults de la plantilla
        for p_name, p_def in param_defs.items():
            resolved[p_name] = p_def.default_value

        # 2. Mapear dimensiones explícitas del AssetSpec
        tot_len_dim = spec.dimensions.get("total_length")
        if tot_len_dim:
            tot = tot_len_dim.target
            resolved["total_length"] = tot
            # Distribuir proporcionalmente: 75% hoja, 18% mango, 4% guarda, 3% pomo
            resolved["blade_length"] = round(tot * 0.75, 4)
            resolved["handle_length"] = round(tot * 0.18, 4)
            resolved["guard_thickness"] = round(tot * 0.04, 4)
            resolved["pommel_size"] = round(tot * 0.03, 4)

        # 3. Proporciones relativas explícitas (ej. blade_to_handle_ratio = 3.0)
        ratio = spec.proportions.get("blade_to_handle_ratio")
        if ratio and "blade_length" in resolved and "handle_length" in resolved:
            resolved["blade_length"] = round(resolved["handle_length"] * ratio, 4)

        return resolved
