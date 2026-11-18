from typing import Dict, Any, List, Optional
from ..core.presentation_types import (
    ProjectionType, CompositionAlignment, LightType,
    BackgroundType, ViewTransformType, PresentationViewAngle,
    InferenceConfidenceLevel, PresentationValidationSeverity
)
from ..core.presentation_schema import (
    CameraConfiguration, FramingSpecification, LightingConfiguration,
    EnvironmentSpec, BackgroundSpec, ColorManagementSpec,
    RenderSettingsSpec, PresentationQualityMetrics, PresentationPreset,
    VisualPresentationContext, PresentationValidationResult
)
from ..engine.camera_lighting_presentation_engine import CameraLightingPresentationEngine

class PresentationMatchingAPI:
    """
    Presentation Matching Engine API (AOE v60)
    
    Regla Fundamental:
    GENERA EL CONTEXTO VISUAL CONTROLADO (VisualPresentationContext - VPC)
    PARA COMPARAR EL ASSET GENERADO CONTRA LA REFERENCIA SIN FALSOS POSITIVOS DE PERSPECTIVA.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = CameraLightingPresentationEngine(engine_version=engine_version)

    def build_presentation_context(
        self,
        geometry: Any,
        surface: Optional[Any] = None,
        reference_analysis: Optional[Any] = None,
        specification: Optional[Any] = None
    ) -> VisualPresentationContext:
        return self._engine.build(geometry, surface, reference_analysis, specification)

    def solve_camera(
        self,
        bounds: Dict[str, Any],
        reference_analysis: Optional[Any] = None,
        projection: ProjectionType = ProjectionType.PERSPECTIVE
    ) -> CameraConfiguration:
        return self._engine.solve_camera(bounds, reference_analysis, projection)

    def build_lighting(
        self,
        distance: float = 3.0,
        reference_analysis: Optional[Any] = None
    ) -> LightingConfiguration:
        return self._engine.build_lighting(distance, reference_analysis)

    def validate_presentation(self, presentation: VisualPresentationContext) -> PresentationValidationResult:
        return self._engine.validate(presentation)

    def regenerate_presentation(
        self,
        targets: List[str],
        context: Dict[str, Any]
    ) -> VisualPresentationContext:
        return self._engine.regenerate(targets, context)

    def compute_presentation_hash(self, presentation: VisualPresentationContext) -> str:
        return self._engine.compute_hash(presentation)
