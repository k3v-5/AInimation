from typing import Dict, List, Tuple
from ..core.intent_schema import Requirement, RequirementStatus

class ConflictResolver:
    @staticmethod
    def resolve_sequential_override(
        previous_requirements: Dict[str, Requirement],
        new_requirements: Dict[str, Requirement]
    ) -> Tuple[Dict[str, Requirement], List[str]]:
        resolved = dict(previous_requirements)
        logs = []

        for req_name, new_req in new_requirements.items():
            if req_name in resolved:
                old_req = resolved[req_name]
                old_req.status = RequirementStatus.OVERRIDDEN
                resolved[f"{req_name}_prev"] = old_req
                logs.append(f"Requirement '{req_name}' ({old_req.value}) was OVERRIDDEN by new value ({new_req.value}).")
            resolved[req_name] = new_req

        return resolved, logs
