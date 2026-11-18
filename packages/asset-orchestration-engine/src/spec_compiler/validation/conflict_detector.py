import re
from typing import Tuple, List

class ConflictDetector:
    @staticmethod
    def detect_conflicts(text: str) -> Tuple[bool, str]:
        t = text.lower()
        # Buscar menciones de múltiples dimensiones contradictorias (ej. "100 cm y 150 cm")
        matches = re.findall(r"(\d+)\s*(cm|m|mm)", t)
        if len(matches) >= 2:
            vals = [m[0] for m in matches]
            if len(set(vals)) > 1 and (" y " in t or " and " in t or " a la vez " in t):
                return True, f"SPECIFICATION_CONFLICT: Contradictory dimensions found: {matches}"
        return False, ""
