"""Thread watchdog and lock dependency cycle / deadlock detection."""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from uaf.runtime_diagnostics.core import SubsystemType


@dataclass
class ThreadHeartbeat:
    thread_id: str
    thread_name: str
    last_heartbeat_time_s: float
    timeout_threshold_s: float
    subsystem: SubsystemType
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LockAcquisition:
    lock_id: str
    owner_thread_id: Optional[str] = None
    waiters: List[str] = field(default_factory=list)
    acquired_time_s: Optional[float] = None


@dataclass
class DeadlockCycle:
    thread_ids: List[str]
    lock_ids: List[str]
    description: str


class ThreadWatchdog:
    """Monitors thread heartbeat pulses and flags stalled threads."""

    def __init__(self, default_timeout_s: float = 5.0) -> None:
        self.default_timeout_s = default_timeout_s
        self._threads: Dict[str, ThreadHeartbeat] = {}

    def register_thread(
        self,
        thread_id: str,
        thread_name: str,
        subsystem: SubsystemType = SubsystemType.GENERAL,
        timeout_threshold_s: Optional[float] = None,
    ) -> None:
        self._threads[thread_id] = ThreadHeartbeat(
            thread_id=thread_id,
            thread_name=thread_name,
            last_heartbeat_time_s=time.perf_counter(),
            timeout_threshold_s=timeout_threshold_s or self.default_timeout_s,
            subsystem=subsystem,
        )

    def unregister_thread(self, thread_id: str) -> None:
        self._threads.pop(thread_id, None)

    def heartbeat(self, thread_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        now = time.perf_counter()
        if thread_id in self._threads:
            self._threads[thread_id].last_heartbeat_time_s = now
            if metadata:
                self._threads[thread_id].metadata.update(metadata)
        else:
            self._threads[thread_id] = ThreadHeartbeat(
                thread_id=thread_id,
                thread_name=f"Thread-{thread_id}",
                last_heartbeat_time_s=now,
                timeout_threshold_s=self.default_timeout_s,
                subsystem=SubsystemType.GENERAL,
                metadata=metadata or {},
            )

    def check_stalls(self, current_time_s: Optional[float] = None) -> List[Dict[str, Any]]:
        now = current_time_s if current_time_s is not None else time.perf_counter()
        stalls: List[Dict[str, Any]] = []

        for tid, hb in self._threads.items():
            elapsed = now - hb.last_heartbeat_time_s
            if elapsed > hb.timeout_threshold_s:
                stalls.append({
                    "thread_id": tid,
                    "thread_name": hb.thread_name,
                    "subsystem": hb.subsystem.value,
                    "stall_duration_s": elapsed,
                    "timeout_threshold_s": hb.timeout_threshold_s,
                    "metadata": dict(hb.metadata),
                })
        return stalls


class DeadlockDetector:
    """Tracks Wait-For graphs between threads and resources to detect deadlocks via cycle detection."""

    def __init__(self) -> None:
        # lock_id -> LockAcquisition
        self._locks: Dict[str, LockAcquisition] = {}

    def lock_acquired(self, lock_id: str, thread_id: str) -> None:
        if lock_id not in self._locks:
            self._locks[lock_id] = LockAcquisition(lock_id=lock_id)
        acq = self._locks[lock_id]
        acq.owner_thread_id = thread_id
        acq.acquired_time_s = time.perf_counter()
        if thread_id in acq.waiters:
            acq.waiters.remove(thread_id)

    def lock_released(self, lock_id: str, thread_id: str) -> None:
        if lock_id in self._locks:
            acq = self._locks[lock_id]
            if acq.owner_thread_id == thread_id:
                acq.owner_thread_id = None
                acq.acquired_time_s = None

    def lock_waiting(self, lock_id: str, thread_id: str) -> None:
        if lock_id not in self._locks:
            self._locks[lock_id] = LockAcquisition(lock_id=lock_id)
        acq = self._locks[lock_id]
        if thread_id not in acq.waiters and acq.owner_thread_id != thread_id:
            acq.waiters.append(thread_id)

    def detect_deadlocks(self) -> List[DeadlockCycle]:
        """Builds directed wait-for graph: thread A -> thread B if A is waiting on a lock owned by B."""
        # Wait-for adjacency list: thread_id -> set of thread_ids it is waiting for
        wait_for: Dict[str, Set[str]] = {}
        # Also map edge (A, B) -> lock_id
        edge_lock: Dict[tuple[str, str], str] = {}

        for lock_id, acq in self._locks.items():
            if acq.owner_thread_id:
                owner = acq.owner_thread_id
                for waiter in acq.waiters:
                    if waiter == owner:
                        continue
                    wait_for.setdefault(waiter, set()).add(owner)
                    edge_lock[(waiter, owner)] = lock_id

        # DFS Cycle Detection
        cycles: List[DeadlockCycle] = []
        visited: Set[str] = set()
        rec_stack: List[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.append(node)

            for neighbor in wait_for.get(node, ()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Cycle found!
                    idx = rec_stack.index(neighbor)
                    cycle_threads = rec_stack[idx:] + [neighbor]
                    cycle_locks: List[str] = []
                    for i in range(len(cycle_threads) - 1):
                        t1 = cycle_threads[i]
                        t2 = cycle_threads[i + 1]
                        cycle_locks.append(edge_lock.get((t1, t2), "unknown_lock"))
                    desc = " -> ".join(
                        f"[{cycle_threads[i]}] waits for lock ({cycle_locks[i]}) held by [{cycle_threads[i+1]}]"
                        for i in range(len(cycle_locks))
                    )
                    cycles.append(DeadlockCycle(
                        thread_ids=cycle_threads[:-1],
                        lock_ids=cycle_locks,
                        description=desc,
                    ))

            rec_stack.pop()

        for t in list(wait_for.keys()):
            if t not in visited:
                dfs(t)

        return cycles

    def clear(self) -> None:
        self._locks.clear()
