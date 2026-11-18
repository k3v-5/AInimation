"""
Global / Ambient Illumination and Static Baking Pipeline for UAF-81.85.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3


@dataclass
class AmbientLighting:
    """
    Ambient illumination representing hemisphere sky/ground diffuse bounce.
    """
    sky_color: Tuple[float, float, float] = (0.05, 0.07, 0.1)      # Linear RGB (upper hemisphere)
    ground_color: Tuple[float, float, float] = (0.02, 0.02, 0.01)  # Linear RGB (lower hemisphere)
    intensity: float = 1.0
    indirect_bounce_scale: float = 1.0

    def __post_init__(self) -> None:
        self.sky_color = ensure_finite_vec3(self.sky_color, "sky_color")
        self.ground_color = ensure_finite_vec3(self.ground_color, "ground_color")
        self.intensity = max(0.0, ensure_finite_scalar(self.intensity, "intensity", 1.0))
        self.indirect_bounce_scale = max(0.0, ensure_finite_scalar(self.indirect_bounce_scale, "indirect_bounce_scale", 1.0))

    def evaluate_hemisphere(self, normal: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Blends sky and ground ambient based on vertical normal component."""
        up_weight = (normal[1] + 1.0) * 0.5  # [-1, 1] -> [0, 1]
        r = (self.sky_color[0] * up_weight + self.ground_color[0] * (1.0 - up_weight)) * self.intensity
        g = (self.sky_color[1] * up_weight + self.ground_color[1] * (1.0 - up_weight)) * self.intensity
        b = (self.sky_color[2] * up_weight + self.ground_color[2] * (1.0 - up_weight)) * self.intensity
        return (round(r, 6), round(g, 6), round(b, 6))


@dataclass
class BakeResult:
    """Result from static lightmap baking."""
    is_valid: bool
    baked_lightmap_count: int
    baked_probe_count: int
    texel_density: float
    cache_hash: str
    errors: List[str] = field(default_factory=list)


class StaticBakePipeline:
    """
    Manages precomputed/baked static lighting generation and validation.
    """

    def __init__(self, target_texel_density: float = 32.0) -> None:
        self.target_texel_density = target_texel_density
        self.cache: Dict[str, BakeResult] = {}

    def validate_uvs(self, uv_channel_count: int, has_overlap: bool) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if uv_channel_count < 2:
            errors.append("Lightmap baking requires at least 2 UV channels (UV1 for lightmaps).")
        if has_overlap:
            errors.append("Overlapping UVs detected in lightmap UV channel.")
        return (len(errors) == 0, errors)

    def bake_scene(
        self,
        scene_id: str,
        static_mesh_count: int,
        static_light_count: int,
        probe_count: int = 100,
        uv_overlap: bool = False
    ) -> BakeResult:
        valid_uv, uv_errors = self.validate_uvs(2, uv_overlap)
        if not valid_uv:
            res = BakeResult(
                is_valid=False,
                baked_lightmap_count=0,
                baked_probe_count=0,
                texel_density=self.target_texel_density,
                cache_hash="",
                errors=uv_errors,
            )
            return res

        payload = f"{scene_id}_{static_mesh_count}_{static_light_count}_{probe_count}"
        chash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        result = BakeResult(
            is_valid=True,
            baked_lightmap_count=static_mesh_count,
            baked_probe_count=probe_count,
            texel_density=self.target_texel_density,
            cache_hash=chash,
        )
        self.cache[scene_id] = result
        return result
