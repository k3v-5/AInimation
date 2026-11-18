"""LiveLink bridge telemetry, latency tracking, and profiling instrumentation.

Integrates with UAF-81.86 profiling and diagnostic infrastructure.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BridgeSpan:
    """Represents a measured span of execution within the bridge pipeline."""
    name: str
    start_time_us: int
    end_time_us: Optional[int] = None
    tags: Dict[str, str] = field(default_factory=dict)
    subsystem: str = "Bridge"

    @property
    def duration_us(self) -> int:
        if self.end_time_us is None:
            return 0
        return max(0, self.end_time_us - self.start_time_us)

    @property
    def duration_ms(self) -> float:
        return self.duration_us / 1000.0

    def finish(self) -> BridgeSpan:
        if self.end_time_us is None:
            self.end_time_us = int(time.perf_counter() * 1_000_000)
        return self


class BridgeTelemetryCollector:
    """Collects runtime telemetry metrics, latency measurements, and queue statistics."""

    def __init__(self) -> None:
        self._spans: List[BridgeSpan] = []
        self._active_spans: Dict[str, BridgeSpan] = {}
        self.messages_sent: int = 0
        self.messages_received: int = 0
        self.bytes_sent: int = 0
        self.bytes_received: int = 0
        self.dropped_messages: int = 0
        self.retransmissions: int = 0
        self.conflicts_detected: int = 0
        self.conflicts_resolved: int = 0
        self.roundtrip_latencies_us: List[int] = []

    def start_span(self, name: str, subsystem: str = "Bridge", tags: Optional[Dict[str, str]] = None) -> BridgeSpan:
        span = BridgeSpan(
            name=name,
            start_time_us=int(time.perf_counter() * 1_000_000),
            tags=tags or {},
            subsystem=subsystem,
        )
        self._active_spans[name] = span
        return span

    def stop_span(self, name: str) -> Optional[BridgeSpan]:
        span = self._active_spans.pop(name, None)
        if span:
            span.finish()
            self._spans.append(span)
            if len(self._spans) > 2000:
                self._spans = self._spans[-1000:]
        return span

    def record_roundtrip(self, latency_us: int) -> None:
        self.roundtrip_latencies_us.append(latency_us)
        if len(self.roundtrip_latencies_us) > 1000:
            self.roundtrip_latencies_us = self.roundtrip_latencies_us[-500:]

    def record_traffic(self, sent_bytes: int = 0, recv_bytes: int = 0) -> None:
        if sent_bytes > 0:
            self.messages_sent += 1
            self.bytes_sent += sent_bytes
        if recv_bytes > 0:
            self.messages_received += 1
            self.bytes_received += recv_bytes

    def get_summary(self) -> Dict[str, Any]:
        avg_rtt_ms = (
            (sum(self.roundtrip_latencies_us) / len(self.roundtrip_latencies_us)) / 1000.0
            if self.roundtrip_latencies_us else 0.0
        )
        p99_rtt_ms = 0.0
        if self.roundtrip_latencies_us:
            sorted_lat = sorted(self.roundtrip_latencies_us)
            p99_idx = int(len(sorted_lat) * 0.99)
            p99_rtt_ms = sorted_lat[min(p99_idx, len(sorted_lat) - 1)] / 1000.0

        return {
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "dropped_messages": self.dropped_messages,
            "retransmissions": self.retransmissions,
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
            "avg_rtt_ms": round(avg_rtt_ms, 3),
            "p99_rtt_ms": round(p99_rtt_ms, 3),
            "completed_spans": len(self._spans),
        }
