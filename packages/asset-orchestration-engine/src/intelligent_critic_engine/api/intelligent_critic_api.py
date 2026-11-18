from typing import Dict, Any, List, Optional
from ..core.critic_types import (
    CausalCategory, CriticPriority, RiskLevel, IterationRecommendation,
    ActionAutonomyLevel
)
from ..core.critic_schema import (
    CriticDiagnosis, RootCause, DefectCluster, ParameterRecommendation,
    CorrectionPlan, CriticConflict, DiagnosticGraph, CriticConfiguration,
    IntelligentCriticResult, CriticValidationResult
)
from ..engine.intelligent_critic_engine import IntelligentCriticEngine

class IntelligentCriticAPI:
    """
    Intelligent Critic API (AOE v63)
    
    Regla Fundamental:
    TRANSFORMA OBSERVACIONES Y DEFECTOS AISLADOS (F61 PERCEPCIÓN + F62 QA GEOMÉTRICO)
    EN UN DIAGNÓSTICO CAUSAL ESTRUCTURADO, IDENTIFICANDO CAUSAS RAÍZ, AGRUPANDO CLUSTERS,
    ESTABLECIENDO PRIORIDADES Y RECOMENDANDO UN PLAN DE CORRECCIÓN PARA F64.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = IntelligentCriticEngine(engine_version=engine_version)

    def generate_critic_diagnosis(
        self,
        visual_specification: Optional[Any] = None,
        geometry_qa: Optional[Any] = None,
        visual_eval: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
        configuration: Optional[CriticConfiguration] = None
    ) -> IntelligentCriticResult:
        return self._engine.critique(visual_specification, geometry_qa, visual_eval, context, configuration)

    def validate_critic_result(self, result: IntelligentCriticResult) -> CriticValidationResult:
        return self._engine.validate_result(result)

    def compute_critic_hash(self, result: IntelligentCriticResult) -> str:
        return self._engine.compute_hash(result)
