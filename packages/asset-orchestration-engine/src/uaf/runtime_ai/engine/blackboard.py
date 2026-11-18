"""
UAF-81.82: Typed, Serializable Blackboard.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional, Set, Tuple
from ..models.definition import BlackboardTypeError, Vec3


ALLOWED_TYPES = (bool, int, float, str, tuple, list, dict)


class Blackboard:
    """
    Deterministic typed key-value memory store for AI agents.
    Disallows unpicklable or volatile runtime objects (e.g. threads, open files).
    """

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store a typed value."""
        if not isinstance(key, str):
            raise BlackboardTypeError(f"Blackboard keys must be strings, got {type(key)}")

        if value is not None and not isinstance(value, ALLOWED_TYPES):
            raise BlackboardTypeError(
                f"Unsupported type '{type(value).__name__}' for Blackboard key '{key}'. "
                f"Supported types: bool, int, float, str, tuple, list, dict."
            )

        self._data[key] = copy.deepcopy(value)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        return key in self._data

    def remove(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False

    def clear(self) -> None:
        self._data.clear()

    def snapshot(self) -> Dict[str, Any]:
        """Return deep copy of current blackboard entries."""
        return copy.deepcopy(self._data)

    def restore(self, data: Dict[str, Any]) -> None:
        self._data = copy.deepcopy(data)
