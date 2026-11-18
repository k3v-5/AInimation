from typing import Dict, Any, Tuple
from ..core.presentation_types import CompositionAlignment
from ..core.presentation_schema import FramingSpecification

class FramingSolver:
    @classmethod
    def solve_framing(
        cls,
        bounds: Dict[str, Any],
        aspect_ratio: float = 1.7778,
        target_occupancy: float = 0.78
    ) -> FramingSpecification:
        # Calcular márgenes seguros
        margin = round((1.0 - target_occupancy) / 2.0, 3)
        margin = max(0.05, margin)

        bbox = (margin, margin, 1.0 - margin, 1.0 - margin)

        return FramingSpecification(
            alignment=CompositionAlignment.CENTER,
            subject_bbox=bbox,
            subject_center=(0.5, 0.5),
            horizontal_margin=margin,
            vertical_margin=margin,
            occupancy_ratio=target_occupancy,
            safe_frame_padding=0.05
        )
