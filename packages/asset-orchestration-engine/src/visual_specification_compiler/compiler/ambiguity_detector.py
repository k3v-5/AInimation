from typing import List, Dict, Any
from ..core.vas_types import AmbiguitySeverity
from ..core.vas_schema import AmbiguityReport

class AmbiguityDetector:
    AMBIGUOUS_PATTERNS = [
        ("más grande", "Relative scale modification without explicit dimensional metric", AmbiguitySeverity.HIGH, "dimensions.scale", ["scale += 20%", "scale = 2.0m"]),
        ("más pequeño", "Relative scale reduction without explicit metric", AmbiguitySeverity.HIGH, "dimensions.scale", ["scale -= 20%", "scale = 0.5m"]),
        ("bastante detalle", "Subjective detail expectation without polygon/texture budget", AmbiguitySeverity.MEDIUM, "detail_requirements.density", ["micro_details = True", "triangles >= 25k"]),
        ("similar a esta imagen", "Vague reference association without target metric", AmbiguitySeverity.MEDIUM, "visual_identity.similarity", ["silhouette_match >= 0.90", "color_match >= 0.85"]),
        ("que se vea realista", "Stylistic ambiguity lacking PBR roughness and subsurface definition", AmbiguitySeverity.LOW, "style_requirements.realism", ["realism_score = 0.95", "stylization_score = 0.05"])
    ]

    @classmethod
    def detect_ambiguities(cls, text: str, instructions: List[str]) -> List[AmbiguityReport]:
        reports = []
        combined_text = (text + " " + " ".join(instructions)).lower()

        for pattern, desc, severity, prop, interps in cls.AMBIGUOUS_PATTERNS:
            if pattern in combined_text:
                reports.append(AmbiguityReport(
                    ambiguity_id=f"AMB_{pattern.replace(' ', '_').upper()}",
                    source_text=pattern,
                    description=desc,
                    severity=severity,
                    affected_property=prop,
                    possible_interpretations=interps,
                    resolution_required=(severity in [AmbiguitySeverity.HIGH, AmbiguitySeverity.CRITICAL])
                ))

        return reports
