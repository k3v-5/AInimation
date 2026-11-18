import uuid
from typing import Dict, Any, List, Optional, Tuple
from ..core.memory_types import PatternState, MemorySource, ProblemSignature, TrustLevel
from ..core.memory_schema import PatternRecord, MemoryEntry
from ..patterns.pattern_matcher import PatternMatcher
from ..patterns.pattern_lifecycle import PatternLifecycleManager
from ..store.memory_store import MemoryStore

class LearnedPatternsAPI:
    """
    Asset Memory & Learned Construction Patterns API (AOE v27)
    
    Regla Fundamental:
    ALMACENA Y REUTILIZA CONOCIMIENTO ESTRUCTURADO DE ÉXITOS Y CORRECCIONES PASADAS.
    REDUCE EL RETRABAJO APLICANDO SOLUCIONES PROBADAS ANTE PROBLEMAS RECURRENTES.
    """
    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()

    def register_pattern(
        self,
        pattern_id: str,
        name: str,
        asset_family: str,
        problem_signature: str,
        target_parameter: str,
        correction_delta: float,
        confidence: float = 0.85,
        builder_version: str = "v1.0.0",
        definition_version: str = "v1.0.0"
    ) -> PatternRecord:
        record = PatternRecord(
            pattern_id=pattern_id,
            name=name,
            asset_family=asset_family,
            problem_signature=problem_signature,
            target_parameter=target_parameter,
            correction_delta=correction_delta,
            confidence=confidence,
            builder_version=builder_version,
            definition_version=definition_version
        )
        self.store.save_pattern(record)
        return record

    def search_patterns(self, query: Dict[str, Any], top_k: int = 5) -> List[Tuple[PatternRecord, float, str]]:
        all_patterns = self.store.list_patterns()
        return PatternMatcher.search_and_rank(all_patterns, query, top_k=top_k)

    def record_outcome(self, pattern_id: str, success: bool, improvement: float = 0.15):
        pat = self.store.get_pattern(pattern_id)
        if pat:
            if success:
                PatternLifecycleManager.record_success(pat, improvement=improvement)
            else:
                PatternLifecycleManager.record_failure(pat)

    def check_conflict(self, pattern_a_id: str, pattern_b_id: str) -> Tuple[bool, str]:
        p_a = self.store.get_pattern(pattern_a_id)
        p_b = self.store.get_pattern(pattern_b_id)
        if not p_a or not p_b:
            return False, "Pattern not found."
        return PatternMatcher.detect_conflicts(p_a, p_b)

    def apply_pattern(
        self,
        pattern: PatternRecord,
        current_parameters: Dict[str, Any],
        auto_apply_threshold: float = 0.90
    ) -> Tuple[bool, Dict[str, Any], str]:
        if pattern.confidence < auto_apply_threshold:
            return False, current_parameters, f"CONFIDENCE_TOO_LOW: Pattern confidence {pattern.confidence:.2f} is below auto-apply threshold {auto_apply_threshold:.2f}; simulation required."

        params = dict(current_parameters)
        curr_v = params.get(pattern.target_parameter, 1.0)
        # Aplicar delta relativo
        new_v = round(curr_v * (1.0 + pattern.correction_delta), 4)
        params[pattern.target_parameter] = new_v
        return True, params, f"Applied pattern '{pattern.name}' ({pattern.target_parameter} -> {new_v})."

    def delete_pattern(self, pattern_id: str):
        self.store.delete_pattern(pattern_id)
