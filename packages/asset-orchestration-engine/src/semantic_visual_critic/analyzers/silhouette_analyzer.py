from typing import Dict, Any, List, Optional
from ..core.critic_types import CriticCameraView

class SilhouetteAnalyzer:
    @classmethod
    def evaluate_multi_view_aspect_ratios(
        cls,
        measured_views: Dict[CriticCameraView, float],
        expected_front: float = 1.52,
        expected_side: float = 1.20,
        tolerance: float = 0.05
    ) -> Dict[str, Any]:
        front_m = measured_views.get(CriticCameraView.FRONT, expected_front)
        side_m = measured_views.get(CriticCameraView.SIDE if hasattr(CriticCameraView, 'SIDE') else CriticCameraView.LEFT, expected_side)

        front_diff = abs(front_m - expected_front)
        side_diff = abs(side_m - expected_side)

        front_ok = front_diff <= tolerance
        side_ok = side_diff <= tolerance

        overall_ok = front_ok and side_ok

        return {
            "front_ok": front_ok,
            "side_ok": side_ok,
            "overall_ok": overall_ok,
            "front_error": round(front_diff, 3),
            "side_error": round(side_diff, 3)
        }
