from typing import Tuple, List

class AmbiguityDetector:
    AMBIGUOUS_WORDS = {"bonito", "bonita", "grande", "pequeño", "pequeña", "épico", "épica", "elegante"}

    @classmethod
    def detect_ambiguity(cls, text: str) -> Tuple[bool, str]:
        t = text.lower().replace(",", " ").replace(".", " ")
        words = set(t.split())
        found_ambig = words.intersection(cls.AMBIGUOUS_WORDS)

        # Si hay palabras ambiguas y ninguna dimensión concreta ni contexto técnico
        has_dimension = any(unit in t for unit in ["cm", "m", "mm", "metros"])
        if found_ambig and not has_dimension:
            return True, f"AMBIGUITY_DETECTED: Ambiguous subjective terms without technical dimension: {list(found_ambig)}"

        return False, ""
