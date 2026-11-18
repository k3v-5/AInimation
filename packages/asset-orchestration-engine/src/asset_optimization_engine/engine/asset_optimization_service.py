import time
from typing import Dict, Any, List, Optional
from ..core.optimization_types import SessionStatus, StrategyType
from ..core.optimization_schema import (
    AssetCost, OptimizationProfile, OptimizationOpportunity,
    OptimizationCandidate, OptimizationSession, OptimizedAssetResult,
    OptimizationValidationResult
)
from ..strategies.strategy_registry import OptimizationStrategyRegistry
from .asset_cost_analyzer import AssetCostAnalyzer
from .opportunity_analyzer import OpportunityAnalyzer
from .candidate_manager import CandidateManager
from .optimization_hasher import OptimizationHasher

class AssetOptimizationService:
    """
    Asset Optimization Service (AOE v67)
    
    Regla Fundamental:
    OPTIMIZA COSTES DE RENDER, GEOMETRÍA, MATERIALES Y MEMORIA VRAM PRESERVANDO LA IDENTIDAD
    VISUAL, SILUETA Y SEMÁNTICA DEL ASSET ACEPTADO POR F66, SIN DEGRADACIÓN EXCESIVA
    Y MANTENIENDO UN BASELINE INMUTABLE.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version
        self.registry = OptimizationStrategyRegistry()

    def optimize_asset(
        self,
        asset_id: str,
        semantic_id: str,
        generated_geometry: Any, # F58
        surface_result: Any,     # F59
        quality_result: Any,     # F66
        profile: Optional[OptimizationProfile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> OptimizedAssetResult:
        ctx = context or {}
        prof = profile or OptimizationProfile()
        session_id = f"OPT_SESS_{asset_id}_{int(time.time()*1000)%100000}"

        # 1. Baseline Inmutable y Análisis de Costes
        baseline_cost = AssetCostAnalyzer.analyze_cost(generated_geometry, surface_result, ctx)
        base_state_hash = getattr(quality_result, "quality_hash", "") or f"HASH_BASE_{asset_id}"

        # 2. Descubrimiento de Oportunidades
        opportunities = OpportunityAnalyzer.find_opportunities(baseline_cost, prof, self.registry, ctx)

        # 3. Generación y Evaluación de Candidatos
        candidates: List[OptimizationCandidate] = []
        for opp in opportunities:
            strat = self.registry.get(opp.strategy_type)
            if strat:
                cand = strat.execute_optimization(opp, baseline_cost, ctx)
                CandidateManager.evaluate_candidate(cand, prof)
                candidates.append(cand)

        # 4. Selección del Mejor Candidato Pareto
        selected = CandidateManager.select_best_candidate(candidates)
        if not selected:
            # Fallback a baseline
            final_cost = baseline_cost
            final_strat = "NONE"
            selected_cand_id = "NONE_BASELINE"
            v_delta = 0.0
            p_delta = 0.0
            m_delta = 0.0
            lods = {}
        else:
            final_cost = selected.cost_after
            final_strat = selected.strategy_type.value
            selected_cand_id = selected.candidate_id
            v_delta = selected.visual_delta
            p_delta = selected.performance_delta
            m_delta = selected.memory_delta
            lods = selected.parameters.get("lods", {})

        opt_hash = OptimizationHasher.compute_optimization_hash(
            asset_id=asset_id,
            baseline_cost_index=baseline_cost.total_cost_index,
            optimized_cost_index=final_cost.total_cost_index,
            selected_strategy=final_strat,
            status="ACCEPTED"
        )

        return OptimizedAssetResult(
            asset_id=asset_id,
            semantic_id=semantic_id,
            baseline_state_hash=base_state_hash,
            optimized_state_hash=f"HASH_OPT_{opt_hash[:12]}",
            optimization_session_id=session_id,
            optimization_profile_id=prof.profile_id,
            selected_candidate_id=selected_cand_id,
            baseline_cost=baseline_cost,
            optimized_cost=final_cost,
            visual_delta=v_delta,
            technical_delta=0.0,
            semantic_delta=0.0,
            performance_delta=p_delta,
            memory_delta=m_delta,
            lod_summary=lods,
            optimization_status="ACCEPTED",
            production_candidate=True,
            optimization_hash=opt_hash,
            generation_metadata={"engine_version": self.engine_version}
        )

    def validate_optimization_result(self, result: OptimizedAssetResult) -> OptimizationValidationResult:
        errors = []
        warnings = []
        if not result.asset_id:
            errors.append("MISSING_ASSET_ID: Asset ID is mandatory.")
        if result.optimized_cost.total_cost_index < 0.0:
            errors.append("INVALID_COST_INDEX: Cost index must be >= 0.")
        return OptimizationValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)
