from typing import Dict, Any, List, Optional, Tuple
from ..core.surface_types import (
    SurfaceTypeTag, ShaderModelType, ColorSpaceType,
    UVUnwrapMethod, BakeChannelType, AttributeSemanticName,
    InvalidationState, SurfaceValidationSeverity
)
from ..core.surface_schema import (
    SurfaceRegion, MaterialDefinition, ShaderGraphSpec,
    MaterialAssignment, UVLayout, TexelDensityReport,
    VertexAttributeSpec, TextureRequirement, BakePlan,
    UnrealMaterialInterface, GeneratedSurfaceResult,
    SurfaceValidationResult
)
from ..engine.material_surface_engine import MaterialSurfaceGenerationEngine

class MaterialSurfaceAPI:
    """
    Material & Surface Generation Engine API (AOE v59)
    
    Regla Fundamental:
    GENERA MATERIALES PBR, ASIGNACIONES SUPERFICIALES, UVs, TEXEL DENSITY Y PLANES DE BAKING
    SIN IMPORTAR DIRECTAMENTE BPY NI DEPENDER DE MCP DIRECTO.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = MaterialSurfaceGenerationEngine(engine_version=engine_version)

    def generate_surface(
        self,
        geometry: Any,
        specification: Optional[Any] = None,
        strategy: Optional[Any] = None,
        generation_seed: int = 42
    ) -> GeneratedSurfaceResult:
        return self._engine.generate(geometry, specification, strategy, generation_seed)

    def generate_material(
        self,
        material_request: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> MaterialDefinition:
        return self._engine.generate_material(material_request, context)

    def generate_uv(
        self,
        geometry: Any,
        uv_strategy: Optional[Dict] = None
    ) -> Tuple[List[UVLayout], TexelDensityReport]:
        return self._engine.generate_uv(geometry, uv_strategy)

    def generate_bake_plan(self, surface_result: GeneratedSurfaceResult) -> BakePlan:
        return self._engine.generate_bake_plan(surface_result)

    def validate_surface(self, result: GeneratedSurfaceResult) -> SurfaceValidationResult:
        return self._engine.validate(result)

    def regenerate_surface(
        self,
        targets: List[str],
        context: Dict[str, Any]
    ) -> GeneratedSurfaceResult:
        return self._engine.regenerate(targets, context)

    def compute_surface_hash(self, result: GeneratedSurfaceResult) -> str:
        return self._engine.compute_hash(result)
