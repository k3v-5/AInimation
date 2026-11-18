from typing import Dict, Any, List, Tuple, Optional
from ..core.spec_types import ConstraintType, ValueType, UnitType, SpecStatus, ApprovalState, RequirementStatus
from ..core.spec_schema import (
    AssetSpec, StyleSpec, VisualIntent, DoorSpec, WindowSpec, StairSpec, SpecBudget,
    RequirementEntry, AssumptionEntry, SpecDiffResult, ImpactAnalysisResult
)
from ..parser.intent_compiler import IntentCompiler
from ..validation.spec_validator import SpecificationValidator
from ..compiler.spec_diff_engine import SpecDiffEngine
from ..compiler.spec_task_compiler import SpecTaskCompiler

class IntentSpecificationAPI:
    """
    Intent Compiler & Specification Language API (AOE v31)
    
    Regla Fundamental:
    NINGUNA INSTRUCCIÓN DE CONSTRUCCIÓN LLEGA DIRECTAMENTE AL MCP.
    LA IA INTERPRETA LENGUAJE NATURAL Y PRODUCE UNA ESPECIFICACIÓN FORMAL (AssetSpec).
    BLENDER Y UNREAL RECIBEN ÚNICAMENTE OPERACIONES DERIVADAS DE UNA ESPECIFICACIÓN VALIDADA.
    """
    @staticmethod
    def compile_intent(prompt: str, spec_id: str = "spec_house_01") -> Tuple[AssetSpec, List[str], List[str]]:
        return IntentCompiler.compile_natural_language_to_spec(prompt, spec_id)

    @staticmethod
    def validate_spec(spec: AssetSpec) -> Tuple[bool, List[str]]:
        return SpecificationValidator.validate_spec(spec)

    @staticmethod
    def diff_and_analyze_impact(old_spec: AssetSpec, new_spec: AssetSpec) -> Tuple[SpecDiffResult, ImpactAnalysisResult]:
        diff = SpecDiffEngine.compare_specs(old_spec, new_spec)
        impact = SpecDiffEngine.perform_impact_analysis(diff)
        return diff, impact

    @staticmethod
    def generate_tasks_from_spec(spec: AssetSpec) -> List[Dict[str, Any]]:
        return SpecTaskCompiler.compile_spec_to_tasks(spec)
