from dataclasses import dataclass, field
from typing import List, Dict, Any
from .intent_schema import BuildSpecification

@dataclass
class IntentTrace:
    raw_text: str
    action: str
    target: str
    requirements_trace: List[Dict[str, Any]] = field(default_factory=list)
    constraints_trace: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "READY"

    @classmethod
    def from_specification(cls, raw_text: str, spec: BuildSpecification) -> 'IntentTrace':
        req_traces = [
            {
                "name": r.name,
                "value": r.value,
                "unit": r.unit,
                "priority": r.priority.value,
                "source": r.source,
                "source_text": r.source_text
            }
            for r in spec.requirements.values()
        ]
        cons_traces = [
            {
                "subject": c.subject,
                "relation": c.relation,
                "object": c.object_target,
                "value": c.value
            }
            for c in spec.constraints
        ]
        return cls(
            raw_text=raw_text,
            action=spec.action.value,
            target=spec.target_type,
            requirements_trace=req_traces,
            constraints_trace=cons_traces,
            status=spec.status.value
        )
