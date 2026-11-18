"""
OperationMetrics model captures computational performance and resource telemetry.
UAF-81.0 Section 32.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class OperationMetrics:
    """
    Performance metrics recorded during operation execution.
    """
    duration_ms: float = 0.0
    cpu_time_ms: float = 0.0
    memory_peak_mb: float = 0.0
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    artifact_count: int = 0
    cache_hit: bool = False
    cache_miss: bool = True
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration_ms": self.duration_ms,
            "cpu_time_ms": self.cpu_time_ms,
            "memory_peak_mb": self.memory_peak_mb,
            "disk_read_bytes": self.disk_read_bytes,
            "disk_write_bytes": self.disk_write_bytes,
            "artifact_count": self.artifact_count,
            "cache_hit": self.cache_hit,
            "cache_miss": self.cache_miss,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationMetrics":
        return cls(
            duration_ms=float(data.get("duration_ms", 0.0)),
            cpu_time_ms=float(data.get("cpu_time_ms", 0.0)),
            memory_peak_mb=float(data.get("memory_peak_mb", 0.0)),
            disk_read_bytes=int(data.get("disk_read_bytes", 0)),
            disk_write_bytes=int(data.get("disk_write_bytes", 0)),
            artifact_count=int(data.get("artifact_count", 0)),
            cache_hit=bool(data.get("cache_hit", False)),
            cache_miss=bool(data.get("cache_miss", True)),
            retry_count=int(data.get("retry_count", 0)),
        )
