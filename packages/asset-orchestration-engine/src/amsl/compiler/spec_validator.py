from typing import Dict, Any, List
from ..core.amsl_types import AMSLAssetType
from ..core.amsl_schema import AssetSpecification

class AMSLValidator:
    VALID_UNITS = {"m", "cm", "mm", "inches", "feet", "deg", "rad", "%"}
    KNOWN_CORE_FIELDS = {
        "specification_id", "schema_version", "asset_id", "semantic_id", "asset_type",
        "category", "purpose", "coordinates", "dimensions", "structure", "components",
        "relationships", "style", "geometry", "materials", "damage", "collision",
        "gameplay", "references", "constraints", "generation", "validation", "quality",
        "provenance", "tags", "metadata", "extensions"
    }

    @classmethod
    def validate_spec(cls, spec: AssetSpecification, raw_dict: Dict[str, Any] = None):
        # 1. Validar campos requeridos
        if not spec.specification_id:
            raise ValueError("INVALID_SPECIFICATION: Missing required field 'specification_id'.")
        if not spec.asset_id:
            raise ValueError("INVALID_SPECIFICATION: Missing required field 'asset_id'.")
        if not spec.schema_version:
            raise ValueError("INVALID_SPECIFICATION: Missing required field 'schema_version'.")
        if not spec.asset_type:
            raise ValueError("INVALID_SPECIFICATION: Missing required field 'asset_type'.")

        # 2. Validar unidades en dimensiones
        dims = spec.dimensions
        for dim_name in ["width", "depth", "height", "length", "diameter", "thickness"]:
            dim_val = getattr(dims, dim_name, None)
            if dim_val:
                if dim_val.unit not in cls.VALID_UNITS:
                    raise ValueError(f"INVALID_UNIT: Unit '{dim_val.unit}' is not recognized in AMSL standard (Allowed: {cls.VALID_UNITS}).")

        # 3. Validar campos desconocidos si se provee raw_dict
        if raw_dict:
            for k in raw_dict.keys():
                if k not in cls.KNOWN_CORE_FIELDS and k not in spec.extensions:
                    raise ValueError(f"SCHEMA_ERROR: Unknown undeclared field '{k}' in specification schema.")

        return True
