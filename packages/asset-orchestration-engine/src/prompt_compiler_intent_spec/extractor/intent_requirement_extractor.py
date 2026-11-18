import re
from typing import Dict, Any, List, Optional, Tuple
from ..core.prompt_types import (
    IntentType, AssetClassType, ProvenanceType,
    RequirementHardness, ConflictSeverity
)
from ..core.prompt_schema import (
    ExtractedComponent, RequirementConflict, AmbiguityRecord
)
from ..normalizer.synonym_registry import SynonymRegistry

class IntentRequirementExtractor:
    @classmethod
    def extract_intent_and_class(cls, text: str) -> Tuple[IntentType, str]:
        t = text.lower()
        
        # Intent
        intent = IntentType.CREATE
        if any(w in t for w in ["modifica", "cambia", "hazlo igual", "mismo pero", "ajusta"]):
            intent = IntentType.MODIFY
        elif any(w in t for w in ["elimina", "borra", "delete"]):
            intent = IntentType.DELETE

        # Asset Class
        asset_class = "OTHER"
        for word in t.split():
            clean_w = re.sub(r'[^\w]', '', word)
            resolved = SynonymRegistry.resolve_asset_class(clean_w)
            if resolved:
                asset_class = resolved
                break

        return intent, asset_class

    @classmethod
    def extract_styles(cls, text: str) -> List[str]:
        t = text.lower()
        styles = []
        if "medieval" in t:
            styles.append("MEDIEVAL")
        if "estilizado" in t or "stylized" in t:
            styles.append("STYLIZED")
        if "low-poly" in t or "low poly" in t:
            styles.append("LOW_POLY")
        if "fotorrealista" in t or "photorealistic" in t:
            styles.append("PHOTOREALISTIC")
        return styles or ["PROJECT_DEFAULT"]

    @classmethod
    def extract_materials(cls, text: str) -> Dict[str, str]:
        t = text.lower()
        mats = {}
        if "madera oscura" in t or "dark wood" in t:
            mats["body"] = "DARK_WOOD"
        elif "madera" in t or "wood" in t:
            mats["body"] = "WOOD"
        if "piedra" in t or "stone" in t:
            mats["walls"] = "STONE"
        if "metal" in t or "metálico" in t or "metálicos" in t:
            mats["rings"] = "METAL"
        return mats

    @classmethod
    def extract_components_and_forbidden(cls, text: str) -> Tuple[Dict[str, int], List[str]]:
        t = text.lower()
        components = {}
        forbidden = []

        # Casos negativos explícitos
        if "sin aros" in t or "sin anillos" in t or "no tenga ningún aro" in t:
            forbidden.append("METAL_RING")

        # Casos positivos explícitos
        if any(w in t for w in ["dos aros", "2 aros", "dos anillos", "2 anillos", "dos bandas", "2 bandas"]):
            if "METAL_RING" not in forbidden:
                components["METAL_RING"] = 2
            else:
                # Contradicción directa
                components["METAL_RING"] = 2

        if "body" not in components and "sin cuerpo" not in t:
            components["BODY"] = 1

        return components, forbidden

    @classmethod
    def extract_gameplay(cls, text: str) -> Tuple[Dict[str, bool], List[str]]:
        t = text.lower()
        flags = {}
        derived = []

        if any(w in t for w in ["recogerlo", "grabbable", "agarrar", "coger"]):
            flags["grabbable"] = True
            derived.append("COLLISION_REQUIRED")
            derived.append("VALID_PIVOT_REQUIRED")
        elif "gameplay" in t:
            flags["gameplay_ready"] = True
            derived.append("COLLISION_REQUIRED")
            derived.append("VALID_PIVOT_REQUIRED")

        return flags, derived

    @classmethod
    def detect_direct_conflicts(cls, text: str, components: Dict[str, int], forbidden: List[str]) -> List[RequirementConflict]:
        t = text.lower()
        conflicts = []

        # Contradicción de tamaño: pequeña pero enorme
        if ("pequeña" in t or "pequeño" in t or "small" in t) and ("enorme" in t or "gigante" in t or "huge" in t):
            conflicts.append(RequirementConflict(
                conflict_id="CONF_SIZE_CONTRADICTION",
                requirement_a="small/pequeña",
                requirement_b="enorme/huge",
                severity=ConflictSeverity.CRITICAL,
                reason="Simultaneous specification of mutually exclusive size descriptors (pequeña vs enorme)."
            ))

        # Contradicción de componentes: dos aros vs sin aros
        if "METAL_RING" in components and "METAL_RING" in forbidden:
            conflicts.append(RequirementConflict(
                conflict_id="CONF_RING_CONTRADICTION",
                requirement_a="2 metal rings requested",
                requirement_b="metal rings forbidden",
                severity=ConflictSeverity.CRITICAL,
                reason="Prompt requests metal rings while explicitly forbidding them."
            ))

        return conflicts
