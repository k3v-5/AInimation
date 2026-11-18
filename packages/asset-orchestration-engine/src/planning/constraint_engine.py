from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import math

@dataclass
class NumericConstraint:
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    exact_val: Optional[float] = None
    approx_val: Optional[float] = None
    tolerance: float = 0.02

class ConstraintEngine:
    def __init__(self):
        self.constraints: Dict[str, NumericConstraint] = {}

    def add_constraint(self, target_key: str, constraint: NumericConstraint):
        self.constraints[target_key] = constraint

    def validate_value(self, target_key: str, value: float) -> Tuple[bool, Optional[str]]:
        if target_key not in self.constraints:
            return True, None

        c = self.constraints[target_key]
        if c.min_val is not None and value < c.min_val:
            return False, f"Value {value} violates minimum constraint ({c.min_val})"
        if c.max_val is not None and value > c.max_val:
            return False, f"Value {value} violates maximum constraint ({c.max_val})"
        if c.exact_val is not None and not math.isclose(value, c.exact_val, abs_tol=c.tolerance):
            return False, f"Value {value} violates exact constraint ({c.exact_val} ± {c.tolerance})"
        if c.approx_val is not None and not math.isclose(value, c.approx_val, rel_tol=0.10):
            return False, f"Value {value} deviates too much from approximate constraint ({c.approx_val})"

        return True, None
