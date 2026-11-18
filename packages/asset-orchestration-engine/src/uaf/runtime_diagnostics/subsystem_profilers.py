"""
Dedicated Subsystem Profilers (Streaming, Physics, AI, Network, Anim, VFX, Lighting, Render, Audio, UI) for UAF-81.86.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StreamingProfileMetrics:
    cells_loaded: int = 0
    cells_unloaded: int = 0
    load_duration_ms: float = 0.0
    io_duration_ms: float = 0.0
    decompression_ms: float = 0.0
    gpu_upload_ms: float = 0.0
    memory_delta_bytes: int = 0
    is_thrashing: bool = False
    cell_io_read_bytes: int = 0
    uncompressed_bytes: int = 0
    io_wait_ms: float = 0.0


class StreamingProfiler:
    def __init__(self) -> None:
        self.history: List[StreamingProfileMetrics] = []

    def record(self, metrics: StreamingProfileMetrics) -> None:
        if (metrics.cells_loaded > 3 and metrics.cells_unloaded > 3) or metrics.io_wait_ms > 5.0:
            metrics.is_thrashing = True
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class PhysicsProfileMetrics:
    broadphase_ms: float = 0.0
    narrowphase_ms: float = 0.0
    solver_ms: float = 0.0
    raycast_count: int = 0
    contact_count: int = 0
    sleeping_bodies: int = 0
    active_bodies: int = 0
    active_rigidbodies: int = 0
    is_explosion_detected: bool = False

    def __post_init__(self) -> None:
        if self.active_rigidbodies and not self.active_bodies:
            self.active_bodies = self.active_rigidbodies


class PhysicsProfiler:
    def __init__(self) -> None:
        self.history: List[PhysicsProfileMetrics] = []

    def record(self, metrics: PhysicsProfileMetrics) -> None:
        if metrics.solver_ms > 10.0 or metrics.contact_count > 5000:
            metrics.is_explosion_detected = True
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class AIProfileMetrics:
    agent_count: int = 0
    active_agents: int = 0
    active_behavior_trees: int = 0
    path_requests: int = 0
    pathfinding_time_ms: float = 0.0
    navmesh_updates: int = 0
    avoidance_ms: float = 0.0
    is_storm_detected: bool = False

    def __post_init__(self) -> None:
        if self.active_agents and not self.agent_count:
            self.agent_count = self.active_agents


class AIProfiler:
    def __init__(self) -> None:
        self.history: List[AIProfileMetrics] = []

    def record(self, metrics: AIProfileMetrics) -> None:
        if metrics.path_requests > 100 or metrics.pathfinding_time_ms > 8.0:
            metrics.is_storm_detected = True
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class NetworkProfileMetrics:
    packets_sent: int = 0
    packets_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    rpc_count: int = 0
    latency_ms: float = 0.0
    packet_loss_percent: float = 0.0
    prediction_corrections: int = 0
    rollback_count: int = 0
    is_anomaly_detected: bool = False


class NetworkProfiler:
    def __init__(self) -> None:
        self.history: List[NetworkProfileMetrics] = []

    def record(self, metrics: NetworkProfileMetrics) -> None:
        if metrics.packet_loss_percent > 10.0 or metrics.prediction_corrections > 50:
            metrics.is_anomaly_detected = True
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class AnimationProfileMetrics:
    skeleton_updates: int = 0
    blend_trees_evaluated: int = 0
    ik_solvers_run: int = 0
    bone_count: int = 0
    animation_cpu_ms: float = 0.0
    hotspot_character_id: Optional[str] = None


class AnimationProfiler:
    def __init__(self) -> None:
        self.history: List[AnimationProfileMetrics] = []

    def record(self, metrics: AnimationProfileMetrics) -> None:
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class VFXProfileMetrics:
    active_emitters: int = 0
    cpu_particles: int = 0
    gpu_particles: int = 0
    simulation_ms: float = 0.0
    draw_calls: int = 0
    vfx_lights: int = 0
    is_leak_detected: bool = False


class VFXProfiler:
    def __init__(self) -> None:
        self.history: List[VFXProfileMetrics] = []

    def record(self, metrics: VFXProfileMetrics) -> None:
        if metrics.active_emitters > 500 or metrics.cpu_particles > 50000:
            metrics.is_leak_detected = True
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class LightingProfileMetrics:
    dynamic_lights: int = 0
    shadow_casters: int = 0
    atlas_occupancy_ratio: float = 0.0
    volumetric_ms: float = 0.0
    postprocess_ms: float = 0.0
    is_overloaded: bool = False


class LightingProfiler:
    def __init__(self) -> None:
        self.history: List[LightingProfileMetrics] = []

    def record(self, metrics: LightingProfileMetrics) -> None:
        if metrics.dynamic_lights > 200 or metrics.atlas_occupancy_ratio > 0.95:
            metrics.is_overloaded = True
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


DiagnosticsVFXProfiler = VFXProfiler
DiagnosticsLightingProfiler = LightingProfiler


@dataclass
class RenderProfileMetrics:
    draw_calls: int = 0
    triangles: int = 0
    vertices: int = 0
    shader_switches: int = 0
    occlusion_culled_ratio: float = 0.0
    render_gpu_ms: float = 0.0


class RenderProfiler:
    def __init__(self) -> None:
        self.history: List[RenderProfileMetrics] = []

    def record(self, metrics: RenderProfileMetrics) -> None:
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class AudioProfileMetrics:
    active_voices: int = 0
    mix_cost_ms: float = 0.0
    dsp_cost_ms: float = 0.0
    streaming_sources: int = 0


class AudioProfiler:
    def __init__(self) -> None:
        self.history: List[AudioProfileMetrics] = []

    def record(self, metrics: AudioProfileMetrics) -> None:
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}


@dataclass
class UIProfileMetrics:
    widget_count: int = 0
    layout_passes: int = 0
    paint_passes: int = 0
    hit_tests: int = 0
    is_layout_thrashing: bool = False


class UIProfiler:
    def __init__(self) -> None:
        self.history: List[UIProfileMetrics] = []

    def record(self, metrics: UIProfileMetrics) -> None:
        if metrics.layout_passes > 10:
            metrics.is_layout_thrashing = True
        self.history.append(metrics)

    def to_dict(self) -> Dict[str, Any]:
        return {"history_samples": len(self.history)}
