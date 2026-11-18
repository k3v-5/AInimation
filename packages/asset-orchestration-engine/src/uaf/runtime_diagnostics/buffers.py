"""
Lock-Free Fixed-Capacity Ring Buffers for UAF-81.86.
"""

from __future__ import annotations
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class TelemetryBuffer(Generic[T]):
    """
    Circular ring buffer with fixed capacity and deterministic overflow policy (overwrite oldest).
    Guarantees bounded memory and continuous rolling history.
    """

    def __init__(self, capacity: int = 1000) -> None:
        self.capacity = max(1, int(capacity))
        self.buffer: List[Optional[T]] = [None] * self.capacity
        self.head: int = 0
        self.size: int = 0
        self.overflow_count: int = 0
        self.is_frozen: bool = False

    def push(self, item: T) -> None:
        """Appends an item to the ring buffer, overwriting the oldest if full."""
        if self.is_frozen:
            return

        if self.size == self.capacity:
            self.overflow_count += 1

        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.capacity
        if self.size < self.capacity:
            self.size += 1

    def to_list(self) -> List[T]:
        return self.snapshot()

    def snapshot(self) -> List[T]:
        """Returns a list of items ordered from oldest to newest."""
        if self.size == 0:
            return []

        if self.size < self.capacity:
            return [self.buffer[i] for i in range(self.size) if self.buffer[i] is not None]  # type: ignore

        # Full buffer: oldest item is at self.head
        result: List[T] = []
        for i in range(self.capacity):
            idx = (self.head + i) % self.capacity
            item = self.buffer[idx]
            if item is not None:
                result.append(item)
        return result

    def freeze(self) -> List[T]:
        """Freezes buffer from further mutations (e.g. on crash/hitch) and returns contents."""
        self.is_frozen = True
        return self.snapshot()

    def unfreeze(self) -> None:
        self.is_frozen = False

    def clear(self) -> None:
        self.buffer = [None] * self.capacity
        self.head = 0
        self.size = 0
        self.overflow_count = 0
        self.is_frozen = False
