"""
Memory Profiler, Ownership Tracking & Leak Detection for UAF-81.86.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .core import AllocationId, SubsystemType


@dataclass
class MemoryAllocation:
    """Represents an active tracked memory allocation."""
    allocation_id: AllocationId
    owner: str
    subsystem: SubsystemType
    resource_type: str
    size_bytes: int
    creation_frame: int
    timestamp: float
    expected_lifetime_frames: Optional[int] = None
    callstack: str = ""
    is_freed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocation_id": self.allocation_id.value,
            "owner": self.owner,
            "subsystem": self.subsystem.value,
            "resource_type": self.resource_type,
            "size_bytes": self.size_bytes,
            "creation_frame": self.creation_frame,
            "timestamp": self.timestamp,
            "expected_lifetime_frames": self.expected_lifetime_frames,
            "callstack": self.callstack,
            "is_freed": self.is_freed,
        }


@dataclass
class MemoryLeakInfo:
    """Represents a diagnosed memory leak."""
    allocation_id: str
    owner: str
    subsystem: SubsystemType
    resource_type: str
    size_bytes: int
    age_frames: int
    expected_lifetime_frames: int
    callstack: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocation_id": self.allocation_id,
            "owner": self.owner,
            "subsystem": self.subsystem.value,
            "resource_type": self.resource_type,
            "size_bytes": self.size_bytes,
            "age_frames": self.age_frames,
            "expected_lifetime_frames": self.expected_lifetime_frames,
            "callstack": self.callstack,
        }


@dataclass
class MemorySnapshot:
    """Immutable memory usage state at a given frame."""
    frame: int
    timestamp: float
    total_allocated_bytes: int
    active_allocations_count: int
    allocations_by_id: Dict[str, MemoryAllocation]
    bytes_by_subsystem: Dict[str, int]
    bytes_by_resource_type: Dict[str, int]


class MemoryProfiler:
    """
    Tracks allocations by subsystem, detects memory leaks, calculates fragmentation,
    and performs snapshot diffing.
    """

    def __init__(self) -> None:
        self.active_allocations: Dict[str, MemoryAllocation] = {}
        self.allocation_counter: int = 0
        self.total_allocated_bytes: int = 0
        self.peak_allocated_bytes: int = 0
        self.total_freed_bytes: int = 0

    def allocate(
        self,
        owner: str,
        subsystem: SubsystemType,
        resource_type: str,
        size_bytes: int,
        frame: int = 0,
        expected_lifetime_frames: Optional[int] = None,
        callstack: str = ""
    ) -> AllocationId:
        self.allocation_counter += 1
        alloc_id = AllocationId(f"alloc_{self.allocation_counter}_{resource_type}")
        size = max(0, int(size_bytes))

        rec = MemoryAllocation(
            allocation_id=alloc_id,
            owner=owner,
            subsystem=subsystem,
            resource_type=resource_type,
            size_bytes=size,
            creation_frame=frame,
            timestamp=time.perf_counter(),
            expected_lifetime_frames=expected_lifetime_frames,
            callstack=callstack,
        )

        self.active_allocations[alloc_id.value] = rec
        self.total_allocated_bytes += size
        if self.total_allocated_bytes > self.peak_allocated_bytes:
            self.peak_allocated_bytes = self.total_allocated_bytes

        return alloc_id

    def free(self, alloc_id: AllocationId) -> bool:
        rec = self.active_allocations.pop(alloc_id.value, None)
        if rec is None:
            return False
        rec.is_freed = True
        self.total_allocated_bytes -= rec.size_bytes
        self.total_freed_bytes += rec.size_bytes
        return True

    def take_snapshot(self, frame: int) -> MemorySnapshot:
        """Captures an immutable snapshot of all currently active allocations."""
        sub_map: Dict[str, int] = {}
        res_map: Dict[str, int] = {}

        for rec in self.active_allocations.values():
            s_key = rec.subsystem.value
            sub_map[s_key] = sub_map.get(s_key, 0) + rec.size_bytes
            res_map[rec.resource_type] = res_map.get(rec.resource_type, 0) + rec.size_bytes

        return MemorySnapshot(
            frame=frame,
            timestamp=time.perf_counter(),
            total_allocated_bytes=self.total_allocated_bytes,
            active_allocations_count=len(self.active_allocations),
            allocations_by_id=dict(self.active_allocations),
            bytes_by_subsystem=sub_map,
            bytes_by_resource_type=res_map,
        )

    def diff_snapshots(
        self,
        snap_a: MemorySnapshot,
        snap_b: MemorySnapshot
    ) -> Dict[str, Any]:
        """Calculates difference in allocations between two snapshots."""
        keys_a = set(snap_a.allocations_by_id.keys())
        keys_b = set(snap_b.allocations_by_id.keys())

        new_keys = keys_b - keys_a
        released_keys = keys_a - keys_b
        retained_keys = keys_a & keys_b

        new_bytes = sum(snap_b.allocations_by_id[k].size_bytes for k in new_keys)
        released_bytes = sum(snap_a.allocations_by_id[k].size_bytes for k in released_keys)
        net_change = snap_b.total_allocated_bytes - snap_a.total_allocated_bytes

        # Growth by subsystem
        sub_growth: Dict[str, int] = {}
        for s_key in set(snap_a.bytes_by_subsystem.keys()) | set(snap_b.bytes_by_subsystem.keys()):
            val_a = snap_a.bytes_by_subsystem.get(s_key, 0)
            val_b = snap_b.bytes_by_subsystem.get(s_key, 0)
            sub_growth[s_key] = val_b - val_a

        return {
            "new_allocations_count": len(new_keys),
            "released_allocations_count": len(released_keys),
            "retained_allocations_count": len(retained_keys),
            "new_bytes": new_bytes,
            "released_bytes": released_bytes,
            "net_byte_change": net_change,
            "growth_by_subsystem": sub_growth,
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_allocated_bytes": self.total_allocated_bytes,
            "peak_allocated_bytes": self.peak_allocated_bytes,
            "total_freed_bytes": self.total_freed_bytes,
            "active_allocations_count": len(self.active_allocations),
        }

    def detect_leaks(self, current_frame: int = 0) -> List[MemoryLeakInfo]:
        """Identifies allocations that have exceeded their declared lifetime."""
        leaks: List[MemoryLeakInfo] = []
        for rec in self.active_allocations.values():
            if rec.expected_lifetime_frames is not None:
                age = current_frame - rec.creation_frame
                if age > rec.expected_lifetime_frames:
                    leaks.append(
                        MemoryLeakInfo(
                            allocation_id=rec.allocation_id.value,
                            owner=rec.owner,
                            subsystem=rec.subsystem,
                            resource_type=rec.resource_type,
                            size_bytes=rec.size_bytes,
                            age_frames=age,
                            expected_lifetime_frames=rec.expected_lifetime_frames,
                            callstack=rec.callstack,
                        )
                    )
        return leaks
