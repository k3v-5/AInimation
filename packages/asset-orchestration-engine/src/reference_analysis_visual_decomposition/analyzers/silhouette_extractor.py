from typing import Dict, Any, Tuple
from ..core.reference_schema import SilhouetteExtraction

class SilhouetteExtractor:
    @classmethod
    def extract_silhouette(cls, image_metadata: Dict[str, Any]) -> SilhouetteExtraction:
        aspect = float(image_metadata.get("aspect_ratio", 1.42))
        complexity = float(image_metadata.get("contour_complexity", 0.35))
        symmetry = image_metadata.get("symmetry", "VERTICAL_Z")
        conf = float(image_metadata.get("confidence", 0.94))

        return SilhouetteExtraction(
            aspect_ratio=round(aspect, 2),
            bounding_box=(0.0, 0.0, 1.0, round(aspect, 2)),
            contour_complexity=complexity,
            symmetry_axis=symmetry,
            silhouette_confidence=conf
        )
