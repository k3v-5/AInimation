from typing import Dict, Any, List, Optional
from ..core.optimization_types import (
    TargetPlatform, TargetEngine, OptimizationObjective,
    NanitePolicy, CollisionPolicy, SessionStatus, StrategyType,
    RiskLevel, BudgetStatus
)
from ..core.optimization_schema import (
    AssetCost, OptimizationProfile, OptimizationOpportunity,
    OptimizationCandidate, OptimizationSession, OptimizedAssetResult,
    OptimizationValidationResult
)
from ..engine.asset_optimization_service import AssetOptimizationService

class AssetOptimizationAPI:
    """
    Asset Optimization API (AOE v67)
    
    Regla Fundamental:
    OPTIMIZA COSTES DE RENDER, GEOMETRÍA, MATERIALES Y MEMORIA VRAM PRESERVANDO LA IDENTIDAD
    VISUAL, SILUETA Y SEMÁNTICA DEL ASSET ACEPTADO POR F66, SIN DEGRADACIÓN EXCESIVA
    Y MANTENIENDO UN BASELINE INMUTABLE.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._service = AssetOptimizationService(engine_version=engine_version)

    def optimize_game_asset(
        self,
        asset_id: str,
        semantic_id: str,
        generated_geometry: Any,
        surface_result: Any,
        quality_result: Any,
        profile: Optional[OptimizationProfile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> OptimizedAssetResult:
        return self._service.optimize_asset(
            asset_id, semantic_id, generated_geometry, surface_result, quality_result, profile, context
        )

    def validate_optimization_result(self, result: OptimizedAssetResult) -> OptimizationValidationResult:
        return self._service.validate_optimization_result(result)
