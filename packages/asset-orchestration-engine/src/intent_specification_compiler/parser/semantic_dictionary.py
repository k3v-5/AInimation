from typing import Dict, List, Optional

class SemanticDictionary:
    SYNONYMS: Dict[str, str] = {
        "pequeña": "SMALL",
        "small": "SMALL",
        "pequeño": "SMALL",
        "reducido": "SMALL",
        "de tamaño reducido": "SMALL",
        "de tamano reducido": "SMALL",
        "vieja": "AGED",
        "viejo": "AGED",
        "aged": "AGED",
        "envejecida": "AGED",
        "inclinada": "SLIGHTLY_LEANING",
        "leaning": "SLIGHTLY_LEANING",
        "medieval": "MEDIEVAL",
        "rural": "MEDIEVAL_RURAL",
        "fantasia": "FANTASY",
        "fantasy": "FANTASY",
        "madera": "WOOD",
        "wood": "WOOD"
    }

    KNOWN_MATERIALS = {"WOOD", "STONE", "THATCH", "IRON", "BRICK", "PLASTER", "LEATHER", "CLOTH"}

    @classmethod
    def normalize_term(cls, term: str) -> str:
        clean = term.lower().strip()
        return cls.SYNONYMS.get(clean, term.upper())

    @classmethod
    def is_known_material(cls, material_name: str) -> bool:
        return material_name.upper() in cls.KNOWN_MATERIALS
