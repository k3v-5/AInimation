"""
BaseRegistry provides a generic, thread-safe registry contract for extension points.
UAF-81.0 Section 51.
"""

import threading
from typing import TypeVar, Generic, Dict, List, Optional, Callable, Any

T = TypeVar("T")


class BaseRegistry(Generic[T]):
    """
    Type-safe registry supporting dynamic lookup, registration, and discovery.
    """
    def __init__(self, name: str = "Registry"):
        self.name = name
        self._entries: Dict[str, T] = {}
        self._lock = threading.RLock()

    def register(self, key: str, item: T, overwrite: bool = False) -> None:
        """Register an item under key. Rejects duplicates if overwrite=False."""
        with self._lock:
            k = str(key).strip()
            if not k:
                raise ValueError(f"{self.name}: Registration key cannot be empty.")
            if k in self._entries and not overwrite:
                raise KeyError(f"{self.name}: Entry '{k}' is already registered.")
            self._entries[k] = item

    def get(self, key: str) -> Optional[T]:
        """Retrieve item by key or None."""
        with self._lock:
            return self._entries.get(str(key).strip())

    def get_or_raise(self, key: str) -> T:
        """Retrieve item by key or raise KeyError."""
        with self._lock:
            item = self.get(key)
            if item is None:
                raise KeyError(f"{self.name}: No entry found for key '{key}'.")
            return item

    def find(self, predicate: Callable[[T], bool]) -> List[T]:
        """Find all items matching a predicate function."""
        with self._lock:
            return [item for item in self._entries.values() if predicate(item)]

    def list(self) -> List[T]:
        """List all registered items."""
        with self._lock:
            return list(self._entries.values())

    def list_keys(self) -> List[str]:
        """List all registered keys."""
        with self._lock:
            return list(self._entries.keys())

    def supports(self, key: str) -> bool:
        """Check if key is registered."""
        with self._lock:
            return str(key).strip() in self._entries

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._entries.clear()
