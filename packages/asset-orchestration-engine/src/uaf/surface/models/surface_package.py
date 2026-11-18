"""
SurfacePackage encapsulates complete, production-ready PBR surface exports.
UAF-81.7 Sections 3, 109.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .surface_definition import SurfaceDefinition
from .material_definition import MaterialDefinition
from .material_instance import MaterialInstance
from .texture_set import TextureSet
from ..uv.uv_definition import UVDefinition
from ..uv.trim_sheet import TrimSheetDefinition
from ..uv.texture_atlas import TextureAtlasDefinition
from ..validation.surface_quality import SurfaceQualityReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class SurfacePackage:
    package_id: str
    surface_definition: SurfaceDefinition
    material_definition: MaterialDefinition
    texture_set: TextureSet
    uv_definition: Optional[UVDefinition] = None
    material_instance: Optional[MaterialInstance] = None
    trim_sheet: Optional[TrimSheetDefinition] = None
    atlas: Optional[TextureAtlasDefinition] = None
    quality_report: Optional[SurfaceQualityReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_id": self.package_id,
            "surface_definition": self.surface_definition.to_dict(),
            "material_definition": self.material_definition.to_dict(),
            "texture_set": self.texture_set.to_dict(),
            "uv_definition": self.uv_definition.to_dict() if self.uv_definition else None,
            "material_instance": self.material_instance.to_dict() if self.material_instance else None,
            "trim_sheet": self.trim_sheet.to_dict() if self.trim_sheet else None,
            "atlas": self.atlas.to_dict() if self.atlas else None,
            "quality_report": self.quality_report.to_dict() if self.quality_report else None,
            "version": self.version,
        }
