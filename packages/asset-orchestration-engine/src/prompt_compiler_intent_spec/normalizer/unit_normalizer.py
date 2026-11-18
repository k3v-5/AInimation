import re
from typing import Dict, Any, Optional

class UnitNormalizer:
    @classmethod
    def parse_percentage_modifier(cls, text: str) -> Optional[float]:
        # Detecta ej. "20% más alto" -> 1.20
        match = re.search(r'(\d+)\s*%\s*(m[aá]s|mayor|higher|more)', text.lower())
        if match:
            percent = float(match.group(1))
            return 1.0 + (percent / 100.0)
        return None
