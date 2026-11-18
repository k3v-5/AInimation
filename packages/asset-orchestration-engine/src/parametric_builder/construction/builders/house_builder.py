from typing import Dict, Any
from ...core.parametric_schema import ParametricAssetDefinition, ParameterDefinition
from ...core.parametric_types import AssetType, ParameterType, ParameterCategory

class MedievalHouseBuilder:
    @staticmethod
    def get_definition() -> ParametricAssetDefinition:
        params = {
            "width": ParameterDefinition("p_w", "width", ParameterType.DISTANCE, ParameterCategory.DIMENSION, 4.0, 1.0, 20.0),
            "depth": ParameterDefinition("p_d", "depth", ParameterType.DISTANCE, ParameterCategory.DIMENSION, 3.5, 1.0, 20.0),
            "height": ParameterDefinition("p_h", "height", ParameterType.DISTANCE, ParameterCategory.DIMENSION, 5.0, 2.0, 25.0),
            "roof_height": ParameterDefinition("p_rh", "roof_height", ParameterType.DISTANCE, ParameterCategory.PROPORTION, 1.75, 0.20, 10.0),
            "roof_angle": ParameterDefinition("p_ra", "roof_angle", ParameterType.ANGLE, ParameterCategory.PROPORTION, 38.0, 15.0, 75.0),
            "window_count": ParameterDefinition("p_wc", "window_count", ParameterType.INTEGER, ParameterCategory.STRUCTURE, 4, 0, 12),
            "window_scale": ParameterDefinition("p_ws", "window_scale", ParameterType.FLOAT, ParameterCategory.STRUCTURE, 1.0, 0.5, 3.0),
            "style": ParameterDefinition("p_st", "style", ParameterType.ENUM, ParameterCategory.STYLE, "stylized")
        }
        return ParametricAssetDefinition(
            asset_type=AssetType.MEDIEVAL_HOUSE,
            version="v1.0.0",
            parameters=params,
            components=["foundation", "walls", "roof", "windows"],
            default_materials={"walls": "plaster_timber", "roof": "wood_shingles", "foundation": "stone"}
        )

    @staticmethod
    def generate_geometry(params: Dict[str, Any]) -> Dict[str, Any]:
        w = params.get("width", 4.0)
        d = params.get("depth", 3.5)
        h = params.get("height", 5.0)
        win_cnt = params.get("window_count", 4)

        # Cálculo determinista de geometría
        v_foundation = 24
        v_walls = 48
        v_roof = 64
        v_windows = win_cnt * 16

        total_v = v_foundation + v_walls + v_roof + v_windows
        total_f = int(total_v * 0.85)

        return {
            "dimensions": {"width": float(w), "depth": float(d), "height": float(h)},
            "geometry_stats": {"vertex_count": total_v, "face_count": total_f},
            "components": ["foundation", "walls", "roof", "windows"],
            "materials": ["stone", "plaster_timber", "wood_shingles"]
        }
