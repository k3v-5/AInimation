import uuid
from typing import Dict, Any, List, Optional, Tuple
from ..core.memory_schema import FailureRecord, CorrectionRecord, StrategyRecord
from ..storage.sqlite_memory_store import SQLiteMemoryStore
from ..analytics.similarity_engine import SimilarityEngine
from ..analytics.confidence_engine import ConfidenceEngine
from ..analytics.pattern_detector import PatternDetector
from ..retrieval.memory_ranker import MemoryRanker
from ..recommendation.generation_advisor import GenerationAdvisor

class AssetMemoryAPI:
    """
    Asset Memory & Learning API (AOE v12)
    
    Regla Fundamental:
    RECORD -> RETRIEVE -> RANK -> RECOMMEND
    NO MODIFICAR BLENDER DIRECTAMENTE DESDE LA MEMORIA.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.store = SQLiteMemoryStore(db_path)

    def register_strategy(
        self,
        strategy_id: str,
        failure_type: str,
        asset_type: str,
        component_type: str,
        preferred_operation: str,
        parameters: Optional[Dict[str, Any]] = None,
        confidence: float = 0.50
    ) -> StrategyRecord:
        strat = StrategyRecord(
            strategy_id=strategy_id,
            failure_type=failure_type,
            asset_type=asset_type,
            component_type=component_type,
            preferred_operation=preferred_operation,
            parameters=parameters or {},
            confidence=confidence
        )
        self.store.store_strategy(strat)
        return strat

    def record_failure(
        self,
        asset_id: str,
        asset_type: str,
        component_type: str,
        failure_type: str,
        actual_val: float,
        expected_val: float,
        metric: str = "ratio"
    ) -> FailureRecord:
        rec = FailureRecord(
            failure_id=f"fail_{uuid.uuid4().hex[:6]}",
            asset_id=asset_id,
            asset_type=asset_type,
            component_type=component_type,
            failure_type=failure_type,
            metric=metric,
            actual_value=actual_val,
            expected_value=expected_val,
            fingerprint=f"{asset_type}:{component_type}:{failure_type}"
        )
        self.store.store_failure(rec)
        return rec

    def record_correction_outcome(
        self,
        failure_id: str,
        strategy_id: str,
        operation_type: str,
        target: str,
        parameters: Dict[str, Any],
        before_score: float,
        after_score: float,
        is_rollback: bool = False
    ) -> Dict[str, Any]:
        is_success = (after_score > before_score) and not is_rollback
        result_str = "ROLLBACK" if is_rollback else ("SUCCESS" if is_success else "FAILURE")

        corr = CorrectionRecord(
            correction_id=f"corr_{uuid.uuid4().hex[:6]}",
            failure_id=failure_id,
            strategy_id=strategy_id,
            operation_type=operation_type,
            target=target,
            parameters=parameters,
            before_score=before_score,
            after_score=after_score,
            result=result_str,
            is_rollback=is_rollback
        )
        self.store.store_correction(corr)

        # Actualizar confianza de la estrategia si existe
        strat = self.store.get_strategy(strategy_id)
        if strat:
            updated_strat = ConfidenceEngine.update_strategy_confidence(strat, is_success, is_rollback)
            self.store.store_strategy(updated_strat)
            return {"recorded": True, "new_confidence": updated_strat.confidence, "success_rate": updated_strat.success_rate}

        return {"recorded": True}

    def retrieve_recommended_strategy(
        self,
        failure_type: str,
        asset_type: str = "SWORD",
        component_type: str = "BLADE"
    ) -> Optional[Dict[str, Any]]:
        strats = self.store.find_strategies(failure_type)
        if not strats:
            # Cold start baseline
            return {
                "memory_hit": False,
                "strategy": "BASELINE_PARAMETRIC_SCALE",
                "preferred_operation": "SET_DIMENSIONS",
                "confidence": 0.50,
                "reason": "Cold start: baseline Phase 11 strategy applied."
            }

        query = {"failure_type": failure_type, "asset_type": asset_type, "component_type": component_type}
        sim_pairs = []
        for s in strats:
            rec_data = {"failure_type": s.failure_type, "asset_type": s.asset_type, "component_type": s.component_type}
            sim = SimilarityEngine.calculate_similarity(query, rec_data)
            sim_pairs.append((s, sim))

        ranked = MemoryRanker.rank_strategies(sim_pairs)
        best_s, best_score = ranked[0]

        return {
            "memory_hit": True,
            "strategy_id": best_s.strategy_id,
            "preferred_operation": best_s.preferred_operation,
            "parameters": best_s.parameters,
            "confidence": best_s.confidence,
            "success_rate": best_s.success_rate,
            "ranking_score": best_score,
            "reason": f"Recommended based on {best_s.sample_count} historical attempts (Success rate: {best_s.success_rate*100:.0f}%)."
        }

    def get_generation_recommendations(self, asset_type: str = "SWORD") -> List[Dict[str, Any]]:
        return GenerationAdvisor.get_generation_recommendations(self.store, asset_type)
