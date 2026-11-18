import hashlib
import json
from typing import Dict, Any, List, Set
from ..core.parametric_types import ParamType, UnitType
from ..core.parametric_schema import ParamDefinition, ResolvedParameters

class ParameterResolver:
    DEFAULT_SCHEMA: Dict[str, ParamDefinition] = {
        "width": ParamDefinition("width", ParamType.FLOAT, UnitType.METERS, default=8.0, minimum=1.0, maximum=50.0, affects=["wall_width", "roof_width"]),
        "depth": ParamDefinition("depth", ParamType.FLOAT, UnitType.METERS, default=6.0, minimum=1.0, maximum=50.0, affects=["wall_depth", "roof_depth"]),
        "wall_height": ParamDefinition("wall_height", ParamType.FLOAT, UnitType.METERS, default=3.0, minimum=1.5, maximum=20.0, affects=["window_z", "roof_z"]),
        "roof_type": ParamDefinition("roof_type", ParamType.ENUM, UnitType.NONE, default="GABLE"),
        "roof_height": ParamDefinition("roof_height", ParamType.FLOAT, UnitType.METERS, default=1.8, minimum=0.5, maximum=10.0),
        "roof_pitch": ParamDefinition("roof_pitch", ParamType.FLOAT, UnitType.DEGREES, default=35.0, minimum=10.0, maximum=75.0),
        "window_count": ParamDefinition("window_count", ParamType.INTEGER, UnitType.COUNT, default=4, minimum=0, maximum=20),
        "door_count": ParamDefinition("door_count", ParamType.INTEGER, UnitType.COUNT, default=1, minimum=1, maximum=5),
        "wall_material": ParamDefinition("wall_material", ParamType.STRING, UnitType.NONE, default="STONE"),
        "roof_material": ParamDefinition("roof_material", ParamType.STRING, UnitType.NONE, default="WOOD"),
    }

    @classmethod
    def resolve_parameters(cls, user_params: Dict[str, Any], schema: Dict[str, ParamDefinition] = None) -> ResolvedParameters:
        s = schema or cls.DEFAULT_SCHEMA
        resolved: Dict[str, Any] = {}

        for k, pdef in s.items():
            if k in user_params:
                val = user_params[k]
                # Validar límites
                if pdef.minimum is not None and val < pdef.minimum:
                    raise ValueError(f"PARAMETER_ERROR: Parameter '{k}' value {val} is below minimum {pdef.minimum}.")
                if pdef.maximum is not None and val > pdef.maximum:
                    raise ValueError(f"PARAMETER_ERROR: Parameter '{k}' value {val} exceeds maximum {pdef.maximum}.")
                resolved[k] = val
            else:
                resolved[k] = pdef.default

        # Parámetros derivados si no se proporcionan explícitamente
        if "roof_ratio" in user_params and "roof_height" not in user_params:
            resolved["roof_height"] = round(resolved["width"] * user_params["roof_ratio"], 2)

        # Hash canónico
        param_str = json.dumps(resolved, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode('utf-8')).hexdigest()[:16]

        return ResolvedParameters(values=resolved, parameter_hash=param_hash)

    @classmethod
    def check_cycles(cls, graph: Dict[str, List[str]]):
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for n in graph:
            if n not in visited:
                if dfs(n):
                    raise ValueError(f"PARAMETER_CYCLE_DETECTED: Dependency cycle detected in parameter graph involving '{n}'.")

class ConstraintSolver:
    @staticmethod
    def solve_constraints(params: Dict[str, Any]):
        w_height = params.get("wall_height", 3.0)
        win_height = params.get("window_height", 1.2)
        win_sill = params.get("window_sill_height", 1.0)

        # Comprobar margen de pared para ventana
        if (win_sill + win_height) >= (w_height - 0.20):
            raise ValueError(f"CONSTRAINT_ERROR: Insufficient wall margin ({win_sill + win_height}m >= {w_height - 0.20}m). Window does not fit on wall.")
