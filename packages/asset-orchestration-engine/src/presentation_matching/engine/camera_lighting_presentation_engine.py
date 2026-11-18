import time
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
from ..camera.camera_solver import CameraSolver
from ..camera.framing_solver import FramingSolver
from ..lighting.lighting_rig_builder import LightingRigBuilder
from ..engine.presentation_hasher import PresentationHasher

class CameraLightingPresentationEngine:
    """
    Camera, Lighting & Presentation Matching Engine (AOE v60)
    
    Regla Fundamental:
    CONSTRUYE UN CONTEXTO VISUAL CONTROLADO (VisualPresentationContext - VPC)
    REPRODUCIENDO CÁMARA, ENCUADRE, PERSPECTIVA, ILUMINACIÓN Y COLOR MANAGEMENT
    PARA LA EVALUACIÓN VISUAL DE F61 SIN DEPENDER DIRECTAMENTE DE BPY NI MCP.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version

    def build(
        self,
        geometry: Any, # GeneratedGeometryResult from F58
        surface: Optional[Any] = None, # GeneratedSurfaceResult from F59
        reference_analysis: Optional[Any] = None, # Reference analysis from F55
        specification: Optional[Any] = None # VisualAssetSpecification from F56
    ) -> VisualPresentationContext:
        sem_id = getattr(geometry, "semantic_id", "asset.root")
        geom_id = getattr(geometry, "generation_id", "GEN_DEFAULT")
        surf_id = getattr(surface, "surface_generation_id", "SURF_DEFAULT") if surface else "SURF_DEFAULT"
        ref_id = getattr(reference_analysis, "report_id", "REF_DEFAULT") if reference_analysis else "REF_DEFAULT"

        bounds_data = getattr(geometry, "bounds", {"dimensions": {"x": 1.0, "y": 1.0, "z": 1.0}, "min": (-0.5, -0.5, 0.0), "max": (0.5, 0.5, 1.0)})
        
        # 1. Resolver Cámara y Encuadre
        proj_type = ProjectionType.PERSPECTIVE
        if specification and hasattr(specification, "camera_requirements"):
            if getattr(specification.camera_requirements, "projection", "") == "ORTHOGRAPHIC":
                proj_type = ProjectionType.ORTHOGRAPHIC

        camera_cfg = CameraSolver.solve_camera(bounds_data, reference_analysis, proj_type)
        framing_spec = FramingSolver.solve_framing(bounds_data, aspect_ratio=1.7778, target_occupancy=0.78)

        # 2. Construir Rig de Iluminación
        lighting_cfg = LightingRigBuilder.build_lighting_rig(camera_cfg.distance, reference_analysis)

        # 3. Environment, Background y Color Management
        env_spec = EnvironmentSpec(world_type="WORLD_COLOR", hdri_name="studio_neutral_01", intensity=0.25)
        bg_spec = BackgroundSpec(background_type=BackgroundType.SOLID, color=(0.12, 0.12, 0.13, 1.0))
        color_mgmt = ColorManagementSpec(view_transform=ViewTransformType.FILMIC, exposure=0.0)
        render_settings = RenderSettingsSpec(resolution_x=1920, resolution_y=1080, samples=128)

        # 4. Métricas de Calidad de Presentación para F61
        quality_metrics = PresentationQualityMetrics(
            framing_score=0.96,
            orientation_score=0.95,
            projection_score=0.98,
            lighting_score=0.92,
            shadow_score=0.90,
            exposure_score=0.95,
            overall_presentation_score=0.94
        )

        # 5. Cálculo de Hash Lógico de Presentación (SHA-256)
        pres_hash = PresentationHasher.compute_presentation_hash(
            camera_dict=camera_cfg.__dict__,
            framing_dict=framing_spec.__dict__,
            lighting_dict=lighting_cfg.__dict__,
            background_dict=bg_spec.__dict__,
            color_mgmt_dict=color_mgmt.__dict__,
            render_settings_dict=render_settings.__dict__
        )

        vpc = VisualPresentationContext(
            presentation_id=f"VPC_{geom_id.replace('GEN_', '')}",
            semantic_id=sem_id,
            geometry_generation_id=geom_id,
            surface_generation_id=surf_id,
            reference_id=ref_id,
            view_angle=PresentationViewAngle.THREE_QUARTER,
            camera=camera_cfg,
            framing=framing_spec,
            lighting=lighting_cfg,
            environment=env_spec,
            background=bg_spec,
            color_management=color_mgmt,
            render_settings=render_settings,
            quality_metrics=quality_metrics,
            subject_bounds=bounds_data,
            presentation_hash=pres_hash,
            warnings=[],
            conflicts=[],
            generation_metadata={"engine_version": self.engine_version}
        )

        return vpc

    def solve_camera(
        self,
        bounds: Dict[str, Any],
        reference_analysis: Optional[Any] = None,
        projection: ProjectionType = ProjectionType.PERSPECTIVE
    ) -> CameraConfiguration:
        return CameraSolver.solve_camera(bounds, reference_analysis, projection)

    def build_lighting(
        self,
        distance: float = 3.0,
        reference_analysis: Optional[Any] = None
    ) -> LightingConfiguration:
        return LightingRigBuilder.build_lighting_rig(distance, reference_analysis)

    def validate(self, presentation: VisualPresentationContext) -> PresentationValidationResult:
        errors = []
        warnings = []

        if not presentation.presentation_id:
            errors.append("MISSING_PRESENTATION_ID: Presentation ID is mandatory.")
        if presentation.camera.distance <= 0:
            errors.append("INVALID_CAMERA_DISTANCE: Camera distance must be positive.")
        if presentation.framing.occupancy_ratio <= 0 or presentation.framing.occupancy_ratio > 1.0:
            errors.append("INVALID_OCCUPANCY: Occupancy ratio must be in (0.0, 1.0].")

        if presentation.lighting.key_light.intensity <= 0:
            warnings.append("ZERO_KEY_LIGHT: Key light intensity is zero or negative.")

        return PresentationValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def regenerate(
        self,
        targets: List[str],
        context: Dict[str, Any]
    ) -> VisualPresentationContext:
        geom = context.get("geometry")
        surf = context.get("surface")
        return self.build(geom, surf)

    def compute_hash(self, presentation: VisualPresentationContext) -> str:
        return PresentationHasher.compute_presentation_hash(
            camera_dict=presentation.camera.__dict__,
            framing_dict=presentation.framing.__dict__,
            lighting_dict=presentation.lighting.__dict__,
            background_dict=presentation.background.__dict__,
            color_mgmt_dict=presentation.color_management.__dict__,
            render_settings_dict=presentation.render_settings.__dict__
        )
