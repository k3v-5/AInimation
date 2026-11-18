"""
UAF-81.83: Input Buffer, Sanitization, and Rate Limiting.
"""

from __future__ import annotations

import collections
from typing import Deque, Dict, List, Optional, Sequence, Tuple

from ..models.definition import (
    InputCommand,
    NumericSecurityError,
    RateLimitExceededError,
    ensure_finite_float,
)


class InputBuffer:
    """
    Buffers, validates, and manages input commands for client prediction
    and server-side execution.
    """

    def __init__(self, max_buffer_size: int = 120, max_inputs_per_tick: int = 10):
        self.max_buffer_size = max_buffer_size
        self.max_inputs_per_tick = max_inputs_per_tick
        self._buffer: Deque[InputCommand] = collections.deque()
        self._inputs_received_this_tick: int = 0

    def add_command(self, cmd: InputCommand) -> None:
        """
        Validate and insert an input command into the buffer.
        Raises NumericSecurityError or RateLimitExceededError on violations.
        """
        self._inputs_received_this_tick += 1
        if self._inputs_received_this_tick > self.max_inputs_per_tick:
            raise RateLimitExceededError(
                f"Exceeded max inputs per tick quota ({self.max_inputs_per_tick})"
            )

        # Validate axes
        for ax in cmd.axes:
            ensure_finite_float(ax, f"InputBuffer.add_command seq={cmd.sequence}")

        # Keep buffer bounded
        if len(self._buffer) >= self.max_buffer_size:
            self._buffer.popleft()

        self._buffer.append(cmd)

    def reset_tick_counter(self) -> None:
        """Reset per-tick rate limit counter."""
        self._inputs_received_this_tick = 0

    def prune_acknowledged(self, last_acked_sequence: int) -> int:
        """
        Remove commands up to and including last_acked_sequence.
        Returns the number of pruned commands.
        """
        pruned = 0
        while self._buffer and self._buffer[0].sequence <= last_acked_sequence:
            self._buffer.popleft()
            pruned += 1
        return pruned

    def get_unacknowledged_commands(self) -> List[InputCommand]:
        """Return a copy of all unacknowledged commands in buffer."""
        return list(self._buffer)

    def pop_oldest(self) -> Optional[InputCommand]:
        """Pop the oldest command from buffer, or None if empty."""
        if self._buffer:
            return self._buffer.popleft()
        return None

    def peek_oldest(self) -> Optional[InputCommand]:
        """Peek at oldest command."""
        if self._buffer:
            return self._buffer[0]
        return None

    def __len__(self) -> int:
        return len(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()
        self._inputs_received_this_tick = 0
