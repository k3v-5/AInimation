import copy
from typing import Dict, Any, Tuple
from ..core.asset_spec import AssetSpec, DimensionValue
from ..core.provenance import AttributeProvenance

class SpecificationPatcher:
    @staticmethod
    def apply_patch(base_spec: AssetSpec, property_path: str, new_value: Any) -> Tuple[AssetSpec, Dict[str, Any]]:
        new_spec = copy.deepcopy(base_spec)
        new_spec.version += 1

        diff = {"property": property_path, "before": None, "after": new_value}

        # Ejemplo de path: "blade.length"
        if property_path == "blade.length":
            if "blade" in new_spec.components:
                prev_val = new_spec.components["blade"].dimensions.get("length")
                diff["before"] = prev_val.target if prev_val else None
                new_spec.components["blade"].dimensions["length"] = DimensionValue(
                    target=float(new_value),
                    provenance=AttributeProvenance.EXPLICIT
                )

        return new_spec, diff
