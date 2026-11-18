from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class AppearanceMetrics:
    material_count: int = 0
    texture_count: int = 0
    uv_set_count: int = 0
    appearance_build_time_ms: float = 0.0

class AppearanceContext:
    def __init__(self):
        self.geometry_locked: bool = True # Bloqueo estricto de geometría en Fase 5
        self.metrics = AppearanceMetrics()

    def lock_geometry(self):
        self.geometry_locked = True

    def unlock_geometry(self):
        self.geometry_locked = False
