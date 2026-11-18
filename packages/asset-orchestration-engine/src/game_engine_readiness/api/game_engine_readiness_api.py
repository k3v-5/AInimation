from typing import Dict, Any, List, Optional
from ..core.readiness_types import (
    ReadinessStatus, EngineTarget, ValidationSeverity,
    PivotMode, CoordinateSystem, NaniteReadinessState
)
from ..core.readiness_schema import (
    EngineProfile, ExportProfile, EngineValidationResult,
    EngineReadinessScore, EngineReadinessManifest, GameEngineReadyAsset,
    ReadinessValidationResult
)
from ..engine.game_engine_readiness_service import GameEngineReadinessService
from ..engine.readiness_manifest_generator import ReadinessManifestGenerator

class GameEngineReadinessAPI:
    """
    Game-Engine Readiness API (AOE v68)
    
    Regla Fundamental:
    VERIFICA RIGUROSAMENTE QUE EL ASSET OPTIMIZADO POR F67 CUMPLA TODOS LOS REQUISITOS
    TÉCNICOS DE UNREAL ENGINE (GEOMETRÍA, MATERIALES, TEXTURAS, TRANSFORMS, PIVOT, UCX, LOD, NANITE)
    ANTES DE PERMITIR SU EMPAQUETADO Y DESPLIEGUE HACIA EL PROYECTO.
    """
    def __init__(self, service_version: str = "1.0.0"):
        self._service = GameEngineReadinessService(service_version=service_version)

    def verify_and_prepare_for_engine(
        self,
        optimized_asset_result: Any,
        engine_profile: Optional[EngineProfile] = None,
        export_profile: Optional[ExportProfile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> GameEngineReadyAsset:
        return self._service.process_readiness(
            optimized_asset_result, engine_profile, export_profile, context
        )

    def validate_engine_ready_asset(self, ready_asset: GameEngineReadyAsset) -> ReadinessValidationResult:
        return self._service.validate_ready_asset(ready_asset)

    def generate_human_report(self, manifest: EngineReadinessManifest) -> str:
        return ReadinessManifestGenerator.format_human_report(manifest)
