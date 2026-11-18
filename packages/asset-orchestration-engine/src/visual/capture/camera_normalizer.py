from .camera_manager import CameraConfig, ViewOrientation

class CameraNormalizer:
    @staticmethod
    def get_normalized_camera(orientation: ViewOrientation, target_bounds: tuple[float, float, float]) -> CameraConfig:
        """
        Calcula una configuración de cámara ortográfica normalizada que centra y encuadra el objeto.
        """
        w, d, h = target_bounds
        max_dim = max(w, d, h, 0.1)
        scale = max_dim * 1.25 # 80% occupancy

        pos_map = {
            ViewOrientation.FRONT: (0.0, -max_dim * 2.0, 0.0),
            ViewOrientation.BACK: (0.0, max_dim * 2.0, 0.0),
            ViewOrientation.LEFT: (-max_dim * 2.0, 0.0, 0.0),
            ViewOrientation.RIGHT: (max_dim * 2.0, 0.0, 0.0),
            ViewOrientation.TOP: (0.0, 0.0, max_dim * 2.0),
            ViewOrientation.BOTTOM: (0.0, 0.0, -max_dim * 2.0),
        }

        return CameraConfig(
            orientation=orientation,
            projection="orthographic",
            position=pos_map.get(orientation, (0.0, -2.5, 0.0)),
            target=(0.0, 0.0, 0.0),
            ortho_scale=scale,
            resolution=(512, 512)
        )
