from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class GoalSpec:
    target_id: str
    required_state: Dict[str, Any] = field(default_factory=dict)
    forbidden_changes: List[str] = field(default_factory=lambda: ["mesh", "material", "unrelated_actors"])

@dataclass
class StateGap:
    is_noop: bool
    missing_capabilities: List[str] = field(default_factory=list)
    modified_properties: Dict[str, Any] = field(default_factory=dict)
    forbidden_conflicts: List[str] = field(default_factory=list)

class GapAnalyzer:
    @staticmethod
    def analyze_gap(current_state: Dict[str, Any], goal: GoalSpec) -> StateGap:
        missing_caps = []
        mod_props = {}

        # Comprobar requerimientos de estado
        for k, expected_v in goal.required_state.items():
            current_v = current_state.get(k)
            if k == "capabilities":
                cur_caps = set(current_v or [])
                for req_c in expected_v:
                    if req_c not in cur_caps:
                        missing_caps.append(req_c)
            elif current_v != expected_v:
                mod_props[k] = {"before": current_v, "after": expected_v}

        is_noop = (len(missing_caps) == 0 and len(mod_props) == 0)
        return StateGap(
            is_noop=is_noop,
            missing_capabilities=missing_caps,
            modified_properties=mod_props
        )
