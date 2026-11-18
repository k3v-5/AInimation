import re
from typing import List, Tuple, Dict, Any
from ..core.asset_spec import ConstraintEntry
from ..core.provenance import AttributeProvenance

class ConstraintExtractor:
    @staticmethod
    def extract_negative_constraints(text: str) -> List[str]:
        t = text.lower()
        negatives = []
        if "sin grabados" in t or "no quiero grabados" in t or "no grabados" in t:
            negatives.append("engraving")
        if "sin gemas" in t or "no gemas" in t:
            negatives.append("gems")
        if "sin fuego" in t or "no fuego" in t or "sin efectos" in t:
            negatives.append("fire_fx")
        return negatives

class RelationExtractor:
    @staticmethod
    def extract_relative_relations(text: str) -> Dict[str, float]:
        t = text.lower()
        proportions = {}
        # Patrón: "tres veces más larga que la empuñadura" o "3 veces"
        if "tres veces" in t or "3 veces" in t or "3x" in t:
            if "empuñadura" in t or "mango" in t or "handle" in t:
                proportions["blade_to_handle_ratio"] = 3.0
        elif "dos veces" in t or "2 veces" in t or "2x" in t:
            if "empuñadura" in t or "mango" in t:
                proportions["blade_to_handle_ratio"] = 2.0
        return proportions
