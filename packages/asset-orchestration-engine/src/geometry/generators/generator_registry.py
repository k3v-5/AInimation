from typing import Dict, Optional
from .base_generator import IGeometryGenerator
from .primitive_generator import PrimitiveGenerator
from .profile_generator import ProfileGenerator

class GeometryGeneratorRegistry:
    def __init__(self):
        self.generators: Dict[str, IGeometryGenerator] = {}
        # Registrar generadores por defecto
        self.register(PrimitiveGenerator())
        self.register(ProfileGenerator())

    def register(self, generator: IGeometryGenerator):
        self.generators[generator.name.lower()] = generator

    def get(self, name: str) -> Optional[IGeometryGenerator]:
        n = name.lower()
        if n in ["box", "cube", "cylinder", "sphere", "cone", "plane"]:
            return self.generators.get("primitive")
        if n in ["blade", "profile", "plate", "panel", "shield"]:
            return self.generators.get("profile")
        return self.generators.get(n)
