"""
Universal Runtime Rendering World Model Definitions (UAF-81.75).
Normative dataclasses, enumerations, and serialization structures for runtime rendering.
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class RenderWorldState(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RENDERING = "RENDERING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class CameraProjection(str, Enum):
    PERSPECTIVE = "PERSPECTIVE"
    ORTHOGRAPHIC = "ORTHOGRAPHIC"


class LightType(str, Enum):
    DIRECTIONAL = "DIRECTIONAL"
    POINT = "POINT"
    SPOT = "SPOT"
    RECT = "RECT"
    AREA = "AREA"


class RenderQueueType(str, Enum):
    BACKGROUND = "BACKGROUND"
    OPAQUE = "OPAQUE"
    ALPHA_TEST = "ALPHA_TEST"
    TRANSPARENT = "TRANSPARENT"
    OVERLAY = "OVERLAY"
    UI = "UI"


class SortMode(str, Enum):
    NONE = "NONE"
    FRONT_TO_BACK = "FRONT_TO_BACK"
    BACK_TO_FRONT = "BACK_TO_FRONT"
    STATE_BUCKET = "STATE_BUCKET"


class ResourceState(str, Enum):
    UNDEFINED = "UNDEFINED"
    UNCREATED = "UNCREATED"
    CREATING = "CREATING"
    READY = "READY"
    IN_USE = "IN_USE"
    RETIRING = "RETIRING"
    RELEASED = "RELEASED"
    FAILED = "FAILED"
    RENDER_TARGET = "RENDER_TARGET"
    DEPTH_STENCIL = "DEPTH_STENCIL"
    SHADER_RESOURCE = "SHADER_RESOURCE"
    COPY_SRC = "COPY_SRC"
    COPY_DST = "COPY_DST"
    PRESENT = "PRESENT"


class BufferType(str, Enum):
    VERTEX = "VERTEX"
    INDEX = "INDEX"
    UNIFORM = "UNIFORM"
    STORAGE = "STORAGE"
    INDIRECT = "INDIRECT"


class TextureFormat(str, Enum):
    RGBA8_UNORM = "RGBA8_UNORM"
    RGBA16F = "RGBA16F"
    RGBA32F = "RGBA32F"
    D32F = "D32F"
    D24S8 = "D24S8"


def copy_dict_deterministic(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: copy_dict_deterministic(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [copy_dict_deterministic(x) for x in data]
    return copy.deepcopy(data)


@dataclass
class RenderCamera:
    camera_id: str
    entity_id: str = ""
    projection: CameraProjection = CameraProjection.PERSPECTIVE
    fov: float = 60.0
    ortho_width: float = 10.0
    near_clip: float = 0.1
    far_clip: float = 1000.0
    aspect_ratio: float = 16.0 / 9.0
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "entity_id": self.entity_id,
            "projection": self.projection.value,
            "fov": round(float(self.fov), 6),
            "ortho_width": round(float(self.ortho_width), 6),
            "near_clip": round(float(self.near_clip), 6),
            "far_clip": round(float(self.far_clip), 6),
            "aspect_ratio": round(float(self.aspect_ratio), 6),
            "position": [round(float(v), 6) for v in self.position],
            "rotation": [round(float(v), 6) for v in self.rotation],
            "is_active": self.is_active,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RenderLight:
    light_id: str
    entity_id: str = ""
    light_type: LightType = LightType.DIRECTIONAL
    color: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    intensity: float = 1.0
    range: float = 10.0
    inner_cone: float = 30.0
    outer_cone: float = 45.0
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    direction: List[float] = field(default_factory=lambda: [0.0, -1.0, 0.0])
    casts_shadows: bool = True
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "light_id": self.light_id,
            "entity_id": self.entity_id,
            "light_type": self.light_type.value,
            "color": [round(float(v), 6) for v in self.color],
            "intensity": round(float(self.intensity), 6),
            "range": round(float(self.range), 6),
            "inner_cone": round(float(self.inner_cone), 6),
            "outer_cone": round(float(self.outer_cone), 6),
            "position": [round(float(v), 6) for v in self.position],
            "direction": [round(float(v), 6) for v in self.direction],
            "casts_shadows": self.casts_shadows,
            "enabled": self.enabled,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RenderMesh:
    mesh_id: str
    vertex_count: int = 0
    index_count: int = 0
    bounds_min: List[float] = field(default_factory=lambda: [-1.0, -1.0, -1.0])
    bounds_max: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    lod_count: int = 1
    lod_distances: List[float] = field(default_factory=lambda: [50.0])
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mesh_id": self.mesh_id,
            "vertex_count": self.vertex_count,
            "index_count": self.index_count,
            "bounds_min": [round(float(v), 6) for v in self.bounds_min],
            "bounds_max": [round(float(v), 6) for v in self.bounds_max],
            "lod_count": self.lod_count,
            "lod_distances": [round(float(v), 6) for v in self.lod_distances],
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RenderMaterial:
    material_id: str
    shader_id: str = "PBR_Default"
    parameters: Dict[str, Any] = field(default_factory=dict)
    textures: Dict[str, str] = field(default_factory=dict)
    render_queue: RenderQueueType = RenderQueueType.OPAQUE
    is_transparent: bool = False
    double_sided: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_id": self.material_id,
            "shader_id": self.shader_id,
            "parameters": copy_dict_deterministic(self.parameters),
            "textures": copy_dict_deterministic(self.textures),
            "render_queue": self.render_queue.value,
            "is_transparent": self.is_transparent,
            "double_sided": self.double_sided,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RenderableEntity:
    renderable_id: str
    entity_id: str
    mesh_id: str
    material_ids: List[str] = field(default_factory=list)
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    bounds_min: List[float] = field(default_factory=lambda: [-1.0, -1.0, -1.0])
    bounds_max: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    visible: bool = True
    layer: int = 1
    cast_shadows: bool = True
    receive_shadows: bool = True
    current_lod: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "renderable_id": self.renderable_id,
            "entity_id": self.entity_id,
            "mesh_id": self.mesh_id,
            "material_ids": list(self.material_ids),
            "position": [round(float(v), 6) for v in self.position],
            "rotation": [round(float(v), 6) for v in self.rotation],
            "scale": [round(float(v), 6) for v in self.scale],
            "bounds_min": [round(float(v), 6) for v in self.bounds_min],
            "bounds_max": [round(float(v), 6) for v in self.bounds_max],
            "visible": self.visible,
            "layer": self.layer,
            "cast_shadows": self.cast_shadows,
            "receive_shadows": self.receive_shadows,
            "current_lod": self.current_lod,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class DrawCommand:
    command_id: str
    renderable_id: str
    mesh_id: str
    material_id: str
    index_count: int
    first_index: int = 0
    sort_key: float = 0.0
    render_queue: RenderQueueType = RenderQueueType.OPAQUE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "renderable_id": self.renderable_id,
            "mesh_id": self.mesh_id,
            "material_id": self.material_id,
            "index_count": self.index_count,
            "first_index": self.first_index,
            "sort_key": round(float(self.sort_key), 6),
            "render_queue": self.render_queue.value,
        }


@dataclass
class RenderPass:
    pass_id: str
    pass_type: str = "ColorPass"
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass_id": self.pass_id,
            "pass_type": self.pass_type,
            "inputs": sorted(list(self.inputs)),
            "outputs": sorted(list(self.outputs)),
            "dependencies": sorted(list(self.dependencies)),
            "enabled": self.enabled,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RenderGraph:
    graph_id: str
    passes: Dict[str, RenderPass] = field(default_factory=dict)
    execution_order: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "passes": {pid: p.to_dict() for pid, p in sorted(self.passes.items())},
            "execution_order": list(self.execution_order),
        }


@dataclass
class GPUResource:
    resource_id: str
    resource_type: str
    size_bytes: int
    state: ResourceState = ResourceState.UNDEFINED
    ref_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "size_bytes": self.size_bytes,
            "state": self.state.value,
            "ref_count": self.ref_count,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RenderFrame:
    frame_index: int
    delta_time: float
    render_time_ms: float = 0.0
    draw_calls_count: int = 0
    triangles_count: int = 0
    culled_objects_count: int = 0
    submitted_commands: List[DrawCommand] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "delta_time": round(float(self.delta_time), 6),
            "render_time_ms": round(float(self.render_time_ms), 6),
            "draw_calls_count": self.draw_calls_count,
            "triangles_count": self.triangles_count,
            "culled_objects_count": self.culled_objects_count,
            "submitted_commands": [cmd.to_dict() for cmd in self.submitted_commands],
        }


@dataclass
class RenderWorldSettings:
    max_draw_commands: int = 10000
    max_lights: int = 256
    max_cameras: int = 16
    max_renderables: int = 50000
    shadow_map_resolution: int = 2048
    enable_hdr: bool = True
    enable_bloom: bool = True
    enable_vsync: bool = True
    buffering_count: int = 2  # Double buffering by default
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_draw_commands": self.max_draw_commands,
            "max_lights": self.max_lights,
            "max_cameras": self.max_cameras,
            "max_renderables": self.max_renderables,
            "shadow_map_resolution": self.shadow_map_resolution,
            "enable_hdr": self.enable_hdr,
            "enable_bloom": self.enable_bloom,
            "enable_vsync": self.enable_vsync,
            "buffering_count": self.buffering_count,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RenderWorld:
    render_world_id: str
    runtime_world_id: str = ""
    state: RenderWorldState = RenderWorldState.CREATED
    settings: RenderWorldSettings = field(default_factory=RenderWorldSettings)
    renderables: Dict[str, RenderableEntity] = field(default_factory=dict)
    cameras: Dict[str, RenderCamera] = field(default_factory=dict)
    active_camera_id: Optional[str] = None
    lights: Dict[str, RenderLight] = field(default_factory=dict)
    materials: Dict[str, RenderMaterial] = field(default_factory=dict)
    meshes: Dict[str, RenderMesh] = field(default_factory=dict)
    render_graph: RenderGraph = field(default_factory=lambda: RenderGraph(graph_id="main_graph"))
    gpu_resources: Dict[str, GPUResource] = field(default_factory=dict)
    frames_rendered: int = 0
    time_seconds: float = 0.0
    destroyed_renderable_ids: Set[str] = field(default_factory=set)
    content_fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "render_world_id": self.render_world_id,
            "runtime_world_id": self.runtime_world_id,
            "state": self.state.value,
            "settings": self.settings.to_dict(),
            "active_camera_id": self.active_camera_id,
            "frames_rendered": self.frames_rendered,
            "time_seconds": round(float(self.time_seconds), 6),
            "renderables": {rid: r.to_dict() for rid, r in sorted(self.renderables.items())},
            "cameras": {cid: c.to_dict() for cid, c in sorted(self.cameras.items())},
            "lights": {lid: l.to_dict() for lid, l in sorted(self.lights.items())},
            "materials": {mid: m.to_dict() for mid, m in sorted(self.materials.items())},
            "meshes": {mid: m.to_dict() for mid, m in sorted(self.meshes.items())},
            "render_graph": self.render_graph.to_dict(),
            "gpu_resources": {gid: g.to_dict() for gid, g in sorted(self.gpu_resources.items())},
        }

    def compute_fingerprint(self) -> str:
        data = self.to_dict()
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.content_fingerprint:
            self.content_fingerprint = self.compute_fingerprint()
