"""
Asynchronous Engine and Task Supervisor for Generative AI Pipelines.

Provides cooperative cancellation tokens, thread pool execution, and non-blocking
task execution with progress reporting.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Callable, Coroutine, Dict, List, Optional, TypeVar

T = TypeVar("T")


class CancellationToken:
    """
    Thread-safe cooperative cancellation token for long-running AI pipelines.
    """

    def __init__(self) -> None:
        self._cancelled: bool = False
        self._lock = threading.Lock()

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        with self._lock:
            return self._cancelled

    def cancel(self) -> None:
        """Trigger cancellation."""
        with self._lock:
            self._cancelled = True

    def reset(self) -> None:
        """Reset cancellation state."""
        with self._lock:
            self._cancelled = False

    def check(self) -> None:
        """Raise asyncio.CancelledError or RuntimeError if cancelled."""
        if self.is_cancelled:
            raise asyncio.CancelledError("Operation was cancelled by user token")


class AsyncTaskSupervisor:
    """
    Supervises background AI jobs, enforcing timeouts and cooperative cancellation.
    """

    def __init__(self) -> None:
        self._active_tokens: Dict[str, CancellationToken] = {}

    def create_token(self, job_id: str) -> CancellationToken:
        """Create and track a cancellation token for a specific job."""
        token = CancellationToken()
        self._active_tokens[job_id] = token
        return token

    def cancel_job(self, job_id: str) -> bool:
        """Request cancellation for an active job."""
        token = self._active_tokens.get(job_id)
        if token:
            token.cancel()
            return True
        return False

    def cleanup(self, job_id: str) -> None:
        """Remove completed job token."""
        self._active_tokens.pop(job_id, None)
