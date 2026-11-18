from typing import Dict, Any, Optional

class SynonymRegistry:
    ASSET_CLASS_SYNONYMS: Dict[str, str] = {
        "barril": "PROP.BARREL",
        "tonel": "PROP.BARREL",
        "barrel": "PROP.BARREL",
        "espada": "WEAPON.SWORD",
        "sword": "WEAPON.SWORD",
        "casa": "BUILDING.HOUSE",
        "house": "BUILDING.HOUSE"
    }

    COMPONENT_SYNONYMS: Dict[str, str] = {
        "aros": "METAL_RING",
        "aro": "METAL_RING",
        "anillos": "METAL_RING",
        "anillo": "METAL_RING",
        "bandas": "METAL_RING",
        "tejado": "ROOF",
        "techo": "ROOF",
        "ventanas": "WINDOW",
        "puerta": "DOOR"
    }

    @classmethod
    def resolve_asset_class(cls, term: str) -> Optional[str]:
        return cls.ASSET_CLASS_SYNONYMS.get(term.lower().strip())

    @classmethod
    def resolve_component(cls, term: str) -> Optional[str]:
        return cls.COMPONENT_SYNONYMS.get(term.lower().strip())
