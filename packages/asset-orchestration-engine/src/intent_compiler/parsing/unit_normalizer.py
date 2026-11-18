import re
from typing import Tuple, Optional

class UnitNormalizer:
    UNIT_REGEX = re.compile(r"(\d+(?:\.\d+)?)\s*(cm|mm|m|metros|centimetros|milimetros)?", re.IGNORECASE)

    @classmethod
    def normalize_dimension(cls, text: str) -> Tuple[bool, Optional[float], str]:
        """
        Devuelve (success, canonical_meters, unit_or_error)
        """
        text = text.strip().lower()

        # Comprobar número sin unidad explícita (ej. "90")
        if re.fullmatch(r"\d+(?:\.\d+)?", text):
            return False, None, "UNIT_AMBIGUITY: Dimension provided without explicit unit (cm, mm, m)."

        m = cls.UNIT_REGEX.search(text)
        if not m:
            return False, None, "INVALID_DIMENSION: Unable to parse dimension."

        val_str, unit = m.group(1), m.group(2)
        val = float(val_str)

        if not unit:
            return False, None, "UNIT_AMBIGUITY: Dimension provided without explicit unit."

        unit = unit.lower()
        if unit in ["cm", "centimetros"]:
            return True, round(val / 100.0, 4), "m"
        elif unit in ["mm", "milimetros"]:
            return True, round(val / 1000.0, 4), "m"
        elif unit in ["m", "metros"]:
            return True, round(val, 4), "m"

        return False, None, f"UNKNOWN_UNIT: Unit '{unit}' is not recognized."
