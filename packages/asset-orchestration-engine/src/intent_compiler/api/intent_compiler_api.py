from typing import Dict, Any, Optional, Tuple, List
from ..core.intent_schema import (
    NaturalLanguageRequest, BuildSpecification, BuildAuthorization, Requirement
)
from ..core.intent_status import SpecStatus
from ..core.intent_trace import IntentTrace
from ..parsing.intent_parser import IntentParser
from ..resolution.conflict_resolver import ConflictResolver
from ..validation.spec_simulator import SpecificationSimulator

class IntentCompilerAPI:
    """
    Intent Compilation & Requirement Resolution API (AOE v21)
    
    Regla Fundamental:
    EL MCP NUNCA INTERPRETA. EL COMPILADOR NORMALIZA, RESUELVE Y AUTORIZA.
    NO CONSTRUIR SI EXISTEN AMBIGÜEDADES BLOQUEANTES O CONFLICTOS SIN RESOLVER.
    """
    def __init__(self):
        pass

    def compile(self, request: NaturalLanguageRequest) -> BuildSpecification:
        return IntentParser.compile_request(request)

    def authorize(self, spec: BuildSpecification) -> BuildAuthorization:
        if spec.status == SpecStatus.READY:
            return BuildAuthorization(authorized=True, status=SpecStatus.READY, spec_id=spec.spec_id)
        return BuildAuthorization(authorized=False, status=spec.status, spec_id=spec.spec_id, reasons=spec.blocking_reasons)

    def simulate(self, spec: BuildSpecification, bounds: Optional[Tuple[float, float]] = None) -> Tuple[bool, List[str]]:
        return SpecificationSimulator.simulate_feasibility(spec, bounds)

    def apply_sequential_override(
        self,
        previous_spec: BuildSpecification,
        new_spec: BuildSpecification
    ) -> BuildSpecification:
        merged_reqs, logs = ConflictResolver.resolve_sequential_override(
            previous_spec.requirements,
            new_spec.requirements
        )
        return BuildSpecification(
            spec_id=new_spec.spec_id,
            action=new_spec.action,
            target_type=new_spec.target_type,
            target_id=new_spec.target_id,
            requirements=merged_reqs,
            constraints=new_spec.constraints,
            status=new_spec.status,
            warnings=logs
        )

    def generate_trace(self, raw_text: str, spec: BuildSpecification) -> IntentTrace:
        return IntentTrace.from_specification(raw_text, spec)
