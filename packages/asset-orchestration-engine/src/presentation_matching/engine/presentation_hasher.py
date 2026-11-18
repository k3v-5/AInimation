import hashlib
import json
from typing import Dict, Any

class PresentationHasher:
    @classmethod
    def compute_presentation_hash(
        cls,
        camera_dict: Dict[str, Any],
        framing_dict: Dict[str, Any],
        lighting_dict: Dict[str, Any],
        background_dict: Dict[str, Any],
        color_mgmt_dict: Dict[str, Any],
        render_settings_dict: Dict[str, Any]
    ) -> str:
        data = {
            "camera": {
                "projection": camera_dict.get("projection"),
                "focal_length": camera_dict.get("focal_length"),
                "position": camera_dict.get("position"),
                "rotation": camera_dict.get("rotation"),
                "orthographic_scale": camera_dict.get("orthographic_scale")
            },
            "framing": {
                "alignment": framing_dict.get("alignment"),
                "occupancy_ratio": framing_dict.get("occupancy_ratio")
            },
            "lighting": {
                "key_intensity": lighting_dict.get("key_light", {}).get("intensity") if isinstance(lighting_dict.get("key_light"), dict) else getattr(getattr(lighting_dict, "key_light", None), "intensity", 0),
                "environment_intensity": lighting_dict.get("environment_intensity") if isinstance(lighting_dict, dict) else getattr(lighting_dict, "environment_intensity", 0)
            },
            "background": {
                "type": background_dict.get("background_type") if isinstance(background_dict, dict) else getattr(background_dict, "background_type", ""),
                "color": background_dict.get("color") if isinstance(background_dict, dict) else getattr(background_dict, "color", ())
            },
            "color_mgmt": {
                "view_transform": color_mgmt_dict.get("view_transform") if isinstance(color_mgmt_dict, dict) else getattr(color_mgmt_dict, "view_transform", ""),
                "exposure": color_mgmt_dict.get("exposure") if isinstance(color_mgmt_dict, dict) else getattr(color_mgmt_dict, "exposure", 0)
            },
            "render_settings": {
                "resolution": (
                    render_settings_dict.get("resolution_x") if isinstance(render_settings_dict, dict) else getattr(render_settings_dict, "resolution_x", 1920),
                    render_settings_dict.get("resolution_y") if isinstance(render_settings_dict, dict) else getattr(render_settings_dict, "resolution_y", 1080)
                )
            }
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
