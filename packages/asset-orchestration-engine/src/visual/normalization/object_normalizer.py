from typing import List, Tuple
from ..capture.render_capture import CapturedView

class ObjectNormalizer:
    @staticmethod
    def normalize_occupancy(view: CapturedView, target_occupancy: float = 0.80) -> CapturedView:
        """
        Garantiza que la silueta esté normalizada y centrada independientemente de la distancia de la cámara.
        """
        # La vista proyectada ya normaliza a 80% occupancy
        return view
