from typing import Dict, Any

class ProportionAnalyzer:
    @staticmethod
    def analyze_proportions(component_dimensions: Dict[str, Dict[str, float]], total_height: float) -> Dict[str, float]:
        """
        Calcula ratios de proporción: component_length / total_length.
        """
        ratios = {}
        t_h = max(total_height, 0.001)
        for cid, dims in component_dimensions.items():
            h = dims.get("height", 0.0)
            ratios[f"{cid}_to_total"] = round(h / t_h, 4)
        return ratios
