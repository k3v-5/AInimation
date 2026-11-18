from typing import Dict, Any, Tuple

class ParameterHierarchySolver:
    @staticmethod
    def solve_parameters(
        template_defaults: Dict[str, Any],
        preset_overrides: Dict[str, Any] = None,
        variant_overrides: Dict[str, Any] = None,
        ai_parameters: Dict[str, Any] = None,
        user_overrides: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Prioridad: USER > EXPLICIT_AI > VARIANT > PRESET > TEMPLATE_DEFAULT > DERIVED
        """
        resolved = dict(template_defaults)

        # 1. Preset
        if preset_overrides:
            resolved.update(preset_overrides)

        # 2. Variant
        if variant_overrides:
            resolved.update(variant_overrides)

        # 3. Explicit AI
        if ai_parameters:
            resolved.update(ai_parameters)

        # 4. User Override
        if user_overrides:
            resolved.update(user_overrides)

        # 5. Derived Parameters (ej. guard_offset = blade_width * 0.15)
        if "blade_width" in resolved:
            resolved["guard_offset"] = round(resolved["blade_width"] * 0.15, 4)

        return True, resolved, "Parameters resolved successfully."
