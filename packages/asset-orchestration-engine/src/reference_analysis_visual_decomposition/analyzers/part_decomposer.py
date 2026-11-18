from typing import Dict, Any, List
from ..core.reference_schema import DecomposedPart

class PartDecomposer:
    @classmethod
    def decompose_parts(cls, asset_hint: str, image_metadata: Dict[str, Any]) -> List[DecomposedPart]:
        parts = []
        raw_parts = image_metadata.get("detected_parts")
        
        if raw_parts:
            for p in raw_parts:
                parts.append(DecomposedPart(
                    part_id=p.get("part_id", f"part_{len(parts)+1}"),
                    semantic_type=p.get("semantic_type", "UNKNOWN"),
                    bounding_box=p.get("bounding_box", (0, 0, 1, 1)),
                    relative_position=p.get("relative_position", (0, 0, 0)),
                    is_primary=p.get("is_primary", True),
                    confidence=p.get("confidence", 0.95)
                ))
        else:
            # Descomposición estándar para barril si no se proporcionan partes directas
            parts = [
                DecomposedPart("part_body", "BODY", (0.0, 0.0, 1.0, 1.42), (0.0, 0.0, 0.0), True, 0.98),
                DecomposedPart("part_ring_top", "RING_01", (0.0, 1.1, 1.02, 0.15), (0.0, 0.0, 1.1), False, 0.95),
                DecomposedPart("part_ring_bottom", "RING_02", (0.0, 0.2, 1.02, 0.15), (0.0, 0.0, 0.2), False, 0.95)
            ]
        return parts
