import re
from typing import Tuple, Optional, Dict, Any
from ..core.asset_spec import DimensionValue
from ..core.provenance import AttributeProvenance

class UnitResolver:
    @staticmethod
    def parse_dimension_from_text(text: str) -> Optional[DimensionValue]:
        t = text.lower()

        # 1. Detectar si es aproximado o exacto
        is_approx = any(w in t for w in ["unos", "alrededor", "aproximadamente", "más o menos", "about"])
        tolerance = 0.05 if is_approx else 0.0
        is_hard = not is_approx

        # 2. Buscar patrones numéricos con unidades (ej. 120 cm, 1.2 m, 35 mm)
        match = re.search(r"(\d+(\.\d+)?)\s*(pulgadas|inches|cm|mm|m)?", t)
        if not match:
            return None

        val = float(match.group(1))
        unit = match.group(3) or "cm" # Default cm si no se especifica

        # Convertir a metros
        target_m = val
        if unit == "cm":
            target_m = val / 100.0
        elif unit == "mm":
            target_m = val / 1000.0
        elif unit in ["pulgadas", "inches"]:
            target_m = (val * 2.54) / 100.0

        target_m = round(target_m, 4)
        min_v = round(target_m * (1.0 - tolerance), 4) if tolerance > 0 else target_m
        max_v = round(target_m * (1.0 + tolerance), 4) if tolerance > 0 else target_m

        return DimensionValue(
            target=target_m,
            tolerance=tolerance,
            min_value=min_v,
            max_value=max_v,
            original_value=val,
            original_unit=unit,
            provenance=AttributeProvenance.EXPLICIT,
            is_hard_constraint=is_hard
        )
