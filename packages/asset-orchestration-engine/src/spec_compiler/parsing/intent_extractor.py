import re
from typing import Dict, Any, Tuple
from ..core.asset_spec import StyleSpecEntry
from ..core.ontology_registry import AssetOntology

class IntentExtractor:
    @staticmethod
    def extract_intent(text: str, ontology: AssetOntology) -> Tuple[str, StyleSpecEntry, float]:
        t = text.lower()
        asset_type = "UNKNOWN"
        conf = 0.5

        # Detectar tipo de asset
        for word in t.replace(",", " ").replace(".", " ").split():
            resolved = ontology.resolve_synonym(word)
            if resolved in ontology.known_asset_types:
                asset_type = resolved
                conf = 0.98
                break

        # Detectar estilo y realismo
        realism = "STYLIZED" if ("estilizada" in t or "stylized" in t) else ("REALISTIC" if "realista" in t else "SEMI_REALISTIC")
        category = "MEDIEVAL" if "medieval" in t else ("SCI_FI" if ("scifi" in t or "futurista" in t) else "FANTASY")

        style = StyleSpecEntry(category=category, realism=realism)
        return asset_type, style, conf
