from .materials.material_schema import MaterialDefinition, PBRParameters, ShaderType
from .materials.material_instance import MaterialInstance
from .materials.material_registry import MaterialRegistry
from .textures.texture_schema import TextureMetadata, TextureUsage, ColorSpace
from .textures.texture_registry import TextureRegistry
from .textures.color_space_validator import ColorSpaceValidator
from .uv.uv_schema import UVSet, UVMethod
from .uv.uv_projection import UVProjection
from .uv.uv_validator import UVValidator
from .assignment.material_assignment import MaterialAssignmentManager, SlotAssignment
from .appearance_qa.appearance_validator import AppearanceValidator
from .appearance_qa.appearance_diff import AppearanceDiff
from .core.appearance_context import AppearanceContext
from .core.appearance_engine import AppearanceEngine
from .api.appearance_api import AppearanceAPI

__all__ = [
    "MaterialDefinition",
    "PBRParameters",
    "ShaderType",
    "MaterialInstance",
    "MaterialRegistry",
    "TextureMetadata",
    "TextureUsage",
    "ColorSpace",
    "TextureRegistry",
    "ColorSpaceValidator",
    "UVSet",
    "UVMethod",
    "UVProjection",
    "UVValidator",
    "MaterialAssignmentManager",
    "SlotAssignment",
    "AppearanceValidator",
    "AppearanceDiff",
    "AppearanceContext",
    "AppearanceEngine",
    "AppearanceAPI"
]
