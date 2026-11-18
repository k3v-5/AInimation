from typing import Dict, Any

class PresentationInvalidationTracker:
    @classmethod
    def handle_camera_change(cls, current_state: Dict[str, Any]) -> Dict[str, str]:
        # Modificar cámara no regenera geometría ni materiales
        return {
            "geometry": "VALID",
            "materials": "VALID",
            "uv_layouts": "VALID",
            "camera": "VALID",
            "lighting": "VALID",
            "presentation_render": "STALE"
        }

    @classmethod
    def handle_lighting_change(cls, current_state: Dict[str, Any]) -> Dict[str, str]:
        # Modificar iluminación no regenera geometría ni UVs
        return {
            "geometry": "VALID",
            "materials": "VALID",
            "uv_layouts": "VALID",
            "camera": "VALID",
            "lighting": "VALID",
            "presentation_render": "STALE"
        }
