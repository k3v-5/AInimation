from typing import Dict, Any, List, Optional

class StyleMaterialAnalyzer:
    @classmethod
    def evaluate_style_and_density(
        cls,
        expected_style: str,
        is_photorealistic: bool,
        detail_density: float
    ) -> Dict[str, Any]:
        has_mismatch = False
        excessive_detail = False

        if "LOW_POLY" in expected_style.upper() or "STYLIZED" in expected_style.upper():
            if is_photorealistic:
                has_mismatch = True
            if detail_density > 0.80:
                excessive_detail = True

        return {
            "has_style_mismatch": has_mismatch,
            "has_excessive_detail": excessive_detail,
            "style_distance": 0.85 if has_mismatch else 0.10
        }
