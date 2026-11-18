from typing import Dict, Any, List
from ..core.reference_schema import LandmarkFeature, ProportionFeature

class FeatureExtractor:
    @staticmethod
    def extract_model_features(model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae proporciones relativas, landmarks y componentes desde datos geométricos/renders.
        """
        dims = model_data.get("dimensions", {"width": 4.0, "depth": 3.5, "height": 5.0})
        w, d, h = dims.get("width", 4.0), dims.get("depth", 3.5), dims.get("height", 5.0)
        comps = model_data.get("components", ["foundation", "walls", "roof", "windows"])

        roof_h = model_data.get("parameters", {}).get("roof_height", 1.75)
        wall_h = h - roof_h
        win_cnt = model_data.get("parameters", {}).get("window_count", 4)
        win_scale = model_data.get("parameters", {}).get("window_scale", 1.0)

        proportions = {
            "roof_to_wall_ratio": ProportionFeature("roof_to_wall_ratio", round(roof_h / max(0.1, wall_h), 3)),
            "width_to_height_ratio": ProportionFeature("width_to_height_ratio", round(w / max(0.1, h), 3)),
            "window_scale": ProportionFeature("window_scale", float(win_scale))
        }

        landmarks = [
            LandmarkFeature("roof_peak", (0.5, 0.5, 1.0)),
            LandmarkFeature("wall_top", (0.5, 0.5, round(wall_h / h, 3))),
            LandmarkFeature("foundation_base", (0.5, 0.5, 0.0))
        ]

        return {
            "proportions": proportions,
            "landmarks": landmarks,
            "components": list(comps),
            "window_count": win_cnt,
            "dimensions": dims
        }
