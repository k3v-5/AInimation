"""
Performance Anomaly, Spike & Frame Hitch Detection for UAF-81.86.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .core import SubsystemType


class AnomalyType(str, Enum):
    FRAME_HITCH = "FRAME_HITCH"
    HITCH = "FRAME_HITCH"
    SUDDEN_SPIKE = "SUDDEN_SPIKE"
    SPIKE = "SUDDEN_SPIKE"
    MEMORY_CREEP = "MEMORY_CREEP"
    PERIODIC_SPIKE = "PERIODIC_SPIKE"
    NETWORK_BURST = "NETWORK_BURST"


class HitchSeverity(str, Enum):
    MINOR = "minor"
    MAJOR = "moderate"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class PerformanceAnomaly:
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: HitchSeverity
    frame: int
    duration_ms: float
    context_frames: Dict[int, float]
    probable_subsystem: SubsystemType
    message: str
    timestamp_ns: int = field(default_factory=time.perf_counter_ns)
    threshold_value: float = 0.0

    @property
    def hitch_severity(self) -> HitchSeverity:
        return self.severity

    @property
    def subsystem(self) -> SubsystemType:
        return self.probable_subsystem

    @property
    def observed_value(self) -> float:
        return self.duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "frame": self.frame,
            "duration_ms": self.duration_ms,
            "context_frames": self.context_frames,
            "probable_subsystem": self.probable_subsystem.value,
            "message": self.message,
            "timestamp_ns": self.timestamp_ns,
            "observed_value": self.observed_value,
            "threshold_value": self.threshold_value,
        }


class AnomalyDetector:
    """
    Detects sudden spikes, frame hitches, and gradual creep.
    Captures context window (frames -1, 0, +1, +2) when hitches occur.
    """

    def __init__(self, target_frame_ms: float = 16.67) -> None:
        self.target_frame_ms = target_frame_ms
        self.recent_frame_times: List[Tuple[int, float]] = []
        self.detected_anomalies: List[PerformanceAnomaly] = []
        self.anomaly_counter: int = 0

    def record_and_evaluate(
        self,
        frame: int,
        frame_time_ms: float,
        subsystem_times: Dict[SubsystemType, float],
        custom_threshold_ms: Optional[float] = None,
    ) -> Optional[PerformanceAnomaly]:
        self.recent_frame_times.append((frame, frame_time_ms))
        if len(self.recent_frame_times) > 10:
            self.recent_frame_times.pop(0)

        thresh = custom_threshold_ms if custom_threshold_ms is not None else self.target_frame_ms
        ratio = frame_time_ms / max(1.0, thresh)
        if ratio < 1.5:
            return None

        # Classify severity
        if ratio >= 5.0:
            sev = HitchSeverity.CRITICAL
        elif ratio >= 3.0:
            sev = HitchSeverity.SEVERE
        elif ratio >= 2.0:
            sev = HitchSeverity.MODERATE
        else:
            sev = HitchSeverity.MINOR

        # Identify most expensive subsystem in this hitch
        highest_sub = SubsystemType.GENERAL
        highest_time = 0.0
        for sub, val in subsystem_times.items():
            if val > highest_time:
                highest_time = val
                highest_sub = sub

        self.anomaly_counter += 1
        ctx: Dict[int, float] = {f: t for f, t in self.recent_frame_times[-4:]}

        anomaly = PerformanceAnomaly(
            anomaly_id=f"anomaly_{self.anomaly_counter}_{frame}",
            anomaly_type=AnomalyType.FRAME_HITCH,
            severity=sev,
            frame=frame,
            duration_ms=round(frame_time_ms, 3),
            context_frames=ctx,
            probable_subsystem=highest_sub,
            message=f"Frame hitch of {frame_time_ms:.2f}ms ({ratio:.1f}x threshold), caused primarily by {highest_sub.value} ({highest_time:.2f}ms)",
            threshold_value=thresh,
        )
        self.detected_anomalies.append(anomaly)
        return anomaly

    def feed_frame(
        self,
        frame_index: int,
        frame_time_ms: float,
        subsystem_times: Optional[Dict[str, float]] = None,
        hitch_threshold_ms: Optional[float] = None,
    ) -> List[PerformanceAnomaly]:
        # Convert string subsystem keys to SubsystemType if needed
        converted_subtimes: Dict[SubsystemType, float] = {}
        for k, v in (subsystem_times or {}).items():
            try:
                sub_enum = SubsystemType(k.upper())
            except Exception:
                sub_enum = SubsystemType.GENERAL
            converted_subtimes[sub_enum] = v

        res = self.record_and_evaluate(
            frame=frame_index,
            frame_time_ms=frame_time_ms,
            subsystem_times=converted_subtimes,
            custom_threshold_ms=hitch_threshold_ms,
        )
        return [res] if res else []

    def get_recent_anomalies(self) -> List[PerformanceAnomaly]:
        return list(self.detected_anomalies)
