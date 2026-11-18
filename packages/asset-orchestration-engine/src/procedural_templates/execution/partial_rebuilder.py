from typing import Dict, Any, Tuple
from ...correction_execution.providers.blender_provider import IBlenderProvider

class PartialRebuilder:
    @staticmethod
    def apply_parameter_patch_and_rebuild(
        asset_id: str,
        target_component: str,
        parameter_name: str,
        new_value: Any,
        provider: IBlenderProvider
    ) -> Tuple[bool, str]:
        """
        Reconstruye ÚNICAMENTE el componente afectado en Blender, sin destruir la escena.
        """
        asset = provider.assets.get(asset_id)
        if not asset or target_component not in asset["components"]:
            return False, f"Component '{target_component}' not found in asset '{asset_id}'."

        comp = asset["components"][target_component]
        curr_dims = list(comp["dimensions"])

        # Mapeo de parámetros a dimensiones
        if parameter_name in ["blade_length", "length"]:
            curr_dims[2] = float(new_value)
        elif parameter_name in ["blade_width", "width"]:
            curr_dims[0] = float(new_value)
        elif parameter_name in ["blade_thickness", "thickness"]:
            curr_dims[1] = float(new_value)

        provider.set_component_dimensions(asset_id, target_component, tuple(curr_dims))
        return True, f"Component '{target_component}' partially rebuilt with {parameter_name}={new_value}."
