from typing import Dict, List, Optional
from .base_validator import IEngineValidator
from .geometry_validator import GeometryValidator
from .material_texture_validator import MaterialTextureValidator
from .transform_pivot_validator import TransformPivotValidator
from .collision_lod_validator import CollisionLODValidator

class EngineValidatorRegistry:
    def __init__(self):
        self._validators: Dict[str, IEngineValidator] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(GeometryValidator())
        self.register(MaterialTextureValidator())
        self.register(TransformPivotValidator())
        self.register(CollisionLODValidator())

    def register(self, validator: IEngineValidator):
        self._validators[validator.validator_id] = validator

    def list_validators(self) -> List[IEngineValidator]:
        return list(self._validators.values())
