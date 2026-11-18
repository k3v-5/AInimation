"""
UAF-81.84.5: Particle Renderers (Sprite, Mesh, Ribbon, Trail, Beam, Decal).
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..emitter.particle import Particle
from ..models.definition import RendererType, SpriteFacing, Vec3


class VFXRenderer:
    """Base abstract particle presentation renderer."""

    def __init__(self, renderer_type: RendererType):
        self.renderer_type = renderer_type

    def render(self, particles: Sequence[Particle]) -> Dict[str, Any]:
        raise NotImplementedError


class SpriteRenderer(VFXRenderer):
    """Renders camera-facing or velocity-aligned 2D quad sprites with flipbooks."""

    def __init__(
        self,
        facing: SpriteFacing = SpriteFacing.BILLBOARD,
        sub_uv_columns: int = 1,
        sub_uv_rows: int = 1,
    ):
        super().__init__(RendererType.SPRITE)
        self.facing = facing
        self.sub_uv_columns = sub_uv_columns
        self.sub_uv_rows = sub_uv_rows

    def render(self, particles: Sequence[Particle]) -> Dict[str, Any]:
        quads = []
        for p in particles:
            if not p.is_alive:
                continue
            quads.append({
                "pos": p.position,
                "size": p.attributes.get("size", (1.0, 1.0, 1.0)),
                "color": p.attributes.get("color", (1.0, 1.0, 1.0, 1.0)),
                "facing": self.facing.value,
                "sprite_idx": p.attributes.get("sprite_index", 0),
            })
        return {
            "type": "sprite",
            "count": len(quads),
            "quads": quads,
        }


class MeshRenderer(VFXRenderer):
    """Renders 3D static mesh instances per particle."""

    def __init__(self, mesh_id: str, material_id: str = "default_mat"):
        super().__init__(RendererType.MESH)
        self.mesh_id = mesh_id
        self.material_id = material_id

    def render(self, particles: Sequence[Particle]) -> Dict[str, Any]:
        instances = []
        for p in particles:
            if not p.is_alive:
                continue
            instances.append({
                "pos": p.position,
                "rot": p.attributes.get("rotation", (0.0, 0.0, 0.0)),
                "scale": p.attributes.get("scale", 1.0),
                "color": p.attributes.get("color", (1.0, 1.0, 1.0, 1.0)),
                "mesh_id": self.mesh_id,
            })
        return {
            "type": "mesh",
            "mesh_id": self.mesh_id,
            "material_id": self.material_id,
            "count": len(instances),
            "instances": instances,
        }


class RibbonRenderer(VFXRenderer):
    """Connects sequential particles into a continuous 3D ribbon."""

    def __init__(self, width: float = 1.0, uv_tiling: float = 1.0):
        super().__init__(RendererType.RIBBON)
        self.width = width
        self.uv_tiling = uv_tiling

    def render(self, particles: Sequence[Particle]) -> Dict[str, Any]:
        nodes = []
        for p in particles:
            if p.is_alive:
                nodes.append({
                    "pos": p.position,
                    "color": p.attributes.get("color", (1.0, 1.0, 1.0, 1.0)),
                    "width": self.width,
                })
        return {
            "type": "ribbon",
            "segment_count": max(0, len(nodes) - 1),
            "nodes": nodes,
        }


class TrailRenderer(VFXRenderer):
    """Maintains historical position paths per particle to generate motion trails."""

    def __init__(self, max_points: int = 20, max_length: float = 50.0):
        super().__init__(RendererType.TRAIL)
        self.max_points = max_points
        self.max_length = max_length
        # Map particle index -> deque of historical positions
        self._history: Dict[int, collections.deque] = {}

    def update_history(self, particles: Sequence[Particle]) -> None:
        active_indices = set()
        for p in particles:
            idx = p.particle_id.index
            active_indices.add(idx)
            if idx not in self._history:
                self._history[idx] = collections.deque(maxlen=self.max_points)
            self._history[idx].append(p.position)

        # Evict dead particle history
        stale = [idx for idx in self._history if idx not in active_indices]
        for idx in stale:
            del self._history[idx]

    def render(self, particles: Sequence[Particle]) -> Dict[str, Any]:
        self.update_history(particles)
        trails = []
        for idx, pts in self._history.items():
            if len(pts) >= 2:
                trails.append(list(pts))
        return {
            "type": "trail",
            "trail_count": len(trails),
            "trails": trails,
        }


class BeamRenderer(VFXRenderer):
    """Renders an energy beam between source and destination endpoints."""

    def __init__(self, source: Vec3 = (0.0, 0.0, 0.0), target: Vec3 = (0.0, 10.0, 0.0), width: float = 1.0):
        super().__init__(RendererType.BEAM)
        self.source = source
        self.target = target
        self.width = width

    def render(self, particles: Sequence[Particle]) -> Dict[str, Any]:
        return {
            "type": "beam",
            "source": self.source,
            "target": self.target,
            "width": self.width,
        }


class DecalRenderer(VFXRenderer):
    """Projects surface decals at particle impact locations."""

    def __init__(self, material_id: str = "decal_mat", size: Vec3 = (2.0, 2.0, 2.0)):
        super().__init__(RendererType.DECAL)
        self.material_id = material_id
        self.size = size

    def render(self, particles: Sequence[Particle]) -> Dict[str, Any]:
        decals = []
        for p in particles:
            if p.is_alive:
                decals.append({
                    "pos": p.position,
                    "normal": p.attributes.get("normal", (0.0, 1.0, 0.0)),
                    "size": self.size,
                    "material_id": self.material_id,
                })
        return {
            "type": "decal",
            "count": len(decals),
            "decals": decals,
        }
