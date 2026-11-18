"""
UAF-81.83: Replicated Property Containers, Quantization, and Dirty Flag Tracking.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Sequence, Tuple

from ..models.definition import ensure_finite_float, ensure_finite_vec3, Vec3


def quantize_value(value: Any, quantization: str) -> Any:
    """
    Quantize numeric values to reduce bandwidth and normalize comparisons.
    Guarantees finite checks and determinism.
    """
    if quantization == "none":
        if isinstance(value, float):
            return ensure_finite_float(value, "quantize_value(none)")
        elif isinstance(value, (list, tuple)) and len(value) == 3 and all(isinstance(x, (int, float)) for x in value):
            return ensure_finite_vec3(value, "quantize_value(none)")
        return value

    if quantization in ("float2", "vec3_2"):
        if isinstance(value, (int, float)):
            val = ensure_finite_float(float(value), "quantize_value(float2)")
            return round(val, 2)
        elif isinstance(value, (list, tuple)) and len(value) == 3:
            vec = ensure_finite_vec3(value, "quantize_value(vec3_2)")
            return (round(vec[0], 2), round(vec[1], 2), round(vec[2], 2))

    if quantization == "float1":
        if isinstance(value, (int, float)):
            val = ensure_finite_float(float(value), "quantize_value(float1)")
            return round(val, 1)
        elif isinstance(value, (list, tuple)) and len(value) == 3:
            vec = ensure_finite_vec3(value, "quantize_value(vec3_1)")
            return (round(vec[0], 1), round(vec[1], 1), round(vec[2], 1))

    if quantization == "int":
        if isinstance(value, (int, float)):
            val = ensure_finite_float(float(value), "quantize_value(int)")
            return int(round(val))

    return value


class PropertyContainer:
    """
    Holds replicated properties for a single network entity with dirty tracking
    and deterministic quantization.
    """

    def __init__(self):
        self._properties: Dict[str, Any] = {}
        self._quantization_rules: Dict[str, str] = {}
        self._dirty_flags: Dict[str, bool] = {}
        self._last_modified_tick: Dict[str, int] = {}

    def register_property(self, name: str, default_value: Any, quantization: str = "none") -> None:
        """Register a replicated property with quantization mode."""
        quantized = quantize_value(default_value, quantization)
        self._quantization_rules[name] = quantization
        self._properties[name] = quantized
        self._dirty_flags[name] = True
        self._last_modified_tick[name] = 0

    def set_property(self, name: str, value: Any, current_tick: int = 0) -> bool:
        """
        Set property value. If value changed after quantization, mark dirty.
        Returns True if property value actually changed.
        """
        rule = self._quantization_rules.get(name, "none")
        quantized = quantize_value(value, rule)

        if name not in self._properties or self._properties[name] != quantized:
            self._properties[name] = quantized
            self._dirty_flags[name] = True
            self._last_modified_tick[name] = current_tick
            return True
        return False

    def get_property(self, name: str, default: Any = None) -> Any:
        """Retrieve property value."""
        return self._properties.get(name, default)

    def get_all_properties(self) -> Dict[str, Any]:
        """Return a copy of all current properties."""
        return dict(self._properties)

    def get_dirty_properties(self) -> Dict[str, Any]:
        """Return all properties currently flagged dirty."""
        return {k: v for k, v in self._properties.items() if self._dirty_flags.get(k, False)}

    def clear_dirty(self, property_names: Optional[Sequence[str]] = None) -> None:
        """Clear dirty flags for specified properties or all if None."""
        if property_names is None:
            for k in self._dirty_flags:
                self._dirty_flags[k] = False
        else:
            for name in property_names:
                if name in self._dirty_flags:
                    self._dirty_flags[name] = False

    def is_dirty(self) -> bool:
        """Check if any property in this container is dirty."""
        return any(self._dirty_flags.values())
