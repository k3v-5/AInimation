from typing import Dict, Any, List

class ParameterResolver:
    @classmethod
    def resolve_parameters(cls, raw_parameters: Dict[str, Any], context_parameters: List[Any]) -> Dict[str, Any]:
        resolved = dict(raw_parameters)
        lookup = {p.parameter_id: p.default_value for p in context_parameters if hasattr(p, "parameter_id")}
        
        for k, v in raw_parameters.items():
            if isinstance(v, str) and v in lookup:
                resolved[k] = lookup[v]
            elif isinstance(v, dict):
                resolved[k] = cls.resolve_parameters(v, context_parameters)
        return resolved
