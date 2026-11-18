import re
from typing import Tuple, Optional, Any, Dict

class TaskUnitNormalizer:
    @staticmethod
    def normalize_dimension(val_str: str) -> Dict[str, Any]:
        """
        Normaliza expresiones como: '20 cm', '+20cm', '0.2m', '8 inches', '+10%', '-10%', 'x1.5', 'half', 'double'.
        """
        s = val_str.lower().strip()

        # 1. Palabras clave relativas
        if s in ["half", "la mitad"]:
            return {"mode": "MULTIPLIER", "value": 0.5}
        if s in ["double", "el doble", "doble"]:
            return {"mode": "MULTIPLIER", "value": 2.0}

        # 2. Multiplicadores tipo x1.5 o 2x
        match_mult = re.match(r'^x\s*([0-9.]+)|([0-9.]+)x$', s)
        if match_mult:
            num = float(match_mult.group(1) or match_mult.group(2))
            return {"mode": "MULTIPLIER", "value": num}

        # 3. Porcentajes (+10%, -10%, 10%)
        match_pct = re.match(r'^([+-]?)\s*([0-9.]+)\s*%$', s)
        if match_pct:
            sign = match_pct.group(1)
            num = float(match_pct.group(2)) / 100.0
            if sign == "-":
                return {"mode": "SCALE_DELTA", "value": 1.0 - num, "raw_pct": -num}
            elif sign == "+":
                return {"mode": "SCALE_DELTA", "value": 1.0 + num, "raw_pct": num}
            else:
                return {"mode": "PERCENTAGE", "value": num}

        # 4. Longitud métrica e imperial
        match_len = re.match(r'^([+-]?)\s*([0-9.]+)\s*(cm|m|mm|inches|in|feet|ft)?$', s)
        if match_len:
            sign = match_len.group(1)
            num = float(match_len.group(2))
            unit = match_len.group(3)

            if not unit:
                # Si no tiene unidad y no es delta claro -> error de ambigüedad
                raise ValueError(f"AMBIGUOUS_UNIT: Value '{val_str}' has no explicit unit (e.g. cm, m, %).")

            if unit == "cm":
                meters = num / 100.0
            elif unit == "mm":
                meters = num / 1000.0
            elif unit in ["inches", "in"]:
                meters = num * 0.0254
            elif unit in ["feet", "ft"]:
                meters = num * 0.3048
            else: # m
                meters = num

            final_val = -meters if sign == "-" else meters
            mode = "DELTA" if sign in ["+", "-"] else "ABSOLUTE"
            return {"mode": mode, "value": round(final_val, 4), "unit": "m"}

        raise ValueError(f"AMBIGUOUS_UNIT: Unable to parse unit expression '{val_str}'.")
