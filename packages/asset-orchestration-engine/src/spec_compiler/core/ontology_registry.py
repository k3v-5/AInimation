from typing import Dict, List, Set

class AssetOntology:
    def __init__(self):
        self.known_asset_types: Set[str] = {"SWORD", "AXE", "SHIELD", "BOW", "STAFF", "PROP", "CHARACTER"}
        self.synonyms: Dict[str, str] = {
            "espada": "SWORD",
            "sword": "SWORD",
            "hacha": "AXE",
            "axe": "AXE",
            "escudo": "SHIELD",
            "shield": "SHIELD",
            "hoja": "blade",
            "filo": "blade",
            "guardia": "guard",
            "guarda": "guard",
            "empuñadura": "grip",
            "mango": "grip",
            "pomo": "pommel"
        }

    def register_asset_type(self, asset_type: str):
        self.known_asset_types.add(asset_type.upper())

    def resolve_synonym(self, word: str) -> str:
        return self.synonyms.get(word.lower(), word.lower())
