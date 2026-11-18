"""
ResourceBudget defines computational, temporal, and spatial thresholds for operations.
UAF-81.0 Section 33.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class ResourceBudget:
    """
    Immutable resource budget constraints.
    """
    max_duration_seconds: float = 300.0
    max_memory_mb: float = 4096.0
    max_disk_mb: float = 10240.0
    max_cpu_percent: float = 100.0
    max_gpu_memory_mb: Optional[float] = None
    max_processes: int = 4

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_duration_seconds": self.max_duration_seconds,
            "max_memory_mb": self.max_memory_mb,
            "max_disk_mb": self.max_disk_mb,
            "max_cpu_percent": self.max_cpu_percent,
            "max_gpu_memory_mb": self.max_gpu_memory_mb,
            "max_processes": self.max_processes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceBudget":
        return cls(
            max_duration_seconds=float(data.get("max_duration_seconds", 300.0)),
            max_memory_mb=float(data.get("max_memory_mb", 4096.0)),
            max_disk_mb=float(data.get("max_disk_mb", 10240.0)),
            max_cpu_percent=float(data.get("max_cpu_percent", 100.0)),
            max_gpu_memory_mb=float(data["max_gpu_memory_mb"]) if data.get("max_gpu_memory_mb") is not None else None,
            max_processes=int(data.get("max_processes", 4)),
        )
