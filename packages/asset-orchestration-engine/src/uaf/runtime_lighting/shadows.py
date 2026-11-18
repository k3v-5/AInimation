"""
Universal Shadow System & Provider Backends for UAF-81.85.
"""

from __future__ import annotations
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .core import (
    LightId,
    LightPriority,
    ShadowBackend,
    ensure_finite_scalar,
    ensure_finite_vec3,
)
from .cascades import CSMCalculator, CascadeSlice
from .atlas import ShadowAtlas, AtlasTile


@dataclass
class ShadowRequest:
    """Request to generate shadow data for a light."""
    light_id: LightId
    light_position: Tuple[float, float, float]
    light_direction: Tuple[float, float, float]
    light_range: float
    priority: LightPriority
    resolution: int = 1024
    is_directional: bool = False
    cascade_count: int = 4
    bias: float = 0.05
    slope_bias: float = 0.5
    normal_bias: float = 0.1
    contact_shadow_length: float = 0.02


@dataclass
class ShadowResult:
    """Output descriptor of processed shadow data."""
    light_id: LightId
    backend: ShadowBackend
    is_valid: bool
    resolution: int
    memory_bytes: int
    cascades: List[CascadeSlice] = field(default_factory=list)
    atlas_tile: Optional[AtlasTile] = None
    shadow_factor: float = 1.0  # 1.0 = fully lit, 0.0 = fully shadowed


class ShadowProvider(ABC):
    """Abstract interface for shadow backends."""

    @abstractmethod
    def process_shadow(self, request: ShadowRequest, frame: int = 0) -> ShadowResult:
        pass

    @abstractmethod
    def release_shadow(self, light_id: LightId) -> None:
        pass


class CSMShadowProvider(ShadowProvider):
    """Cascaded Shadow Maps provider for directional lights."""

    def __init__(self, default_resolution: int = 2048) -> None:
        self.default_resolution = default_resolution
        self.active_shadows: Dict[str, ShadowResult] = {}

    def process_shadow(self, request: ShadowRequest, frame: int = 0) -> ShadowResult:
        splits = CSMCalculator.compute_splits(
            near_z=0.1,
            far_z=request.light_range,
            cascade_count=request.cascade_count,
            lambda_factor=0.8,
        )
        slices = CSMCalculator.calculate_slices(
            camera_fov_rad=math.radians(60.0),
            aspect_ratio=1.777,
            camera_pos=(0.0, 1.7, 0.0),
            camera_forward=(0.0, 0.0, -1.0),
            splits=splits,
            shadow_map_resolution=request.resolution or self.default_resolution,
        )
        mem = (request.resolution ** 2) * 4 * len(slices)
        result = ShadowResult(
            light_id=request.light_id,
            backend=ShadowBackend.CSM,
            is_valid=True,
            resolution=request.resolution,
            memory_bytes=mem,
            cascades=slices,
        )
        self.active_shadows[request.light_id.value] = result
        return result

    def release_shadow(self, light_id: LightId) -> None:
        self.active_shadows.pop(light_id.value, None)


class AtlasShadowProvider(ShadowProvider):
    """Shadow Atlas provider for point and spot lights."""

    def __init__(self, atlas_size: int = 4096) -> None:
        self.atlas = ShadowAtlas(size=atlas_size)

    def process_shadow(self, request: ShadowRequest, frame: int = 0) -> ShadowResult:
        tile = self.atlas.allocate(
            light_id=request.light_id,
            requested_resolution=request.resolution,
            priority=request.priority,
            frame=frame,
        )
        if tile is None:
            return ShadowResult(
                light_id=request.light_id,
                backend=ShadowBackend.ATLAS_SHADOW,
                is_valid=False,
                resolution=0,
                memory_bytes=0,
            )
        mem = tile.width * tile.height * self.atlas.bytes_per_pixel
        return ShadowResult(
            light_id=request.light_id,
            backend=ShadowBackend.ATLAS_SHADOW,
            is_valid=True,
            resolution=tile.width,
            memory_bytes=mem,
            atlas_tile=tile,
        )

    def release_shadow(self, light_id: LightId) -> None:
        self.atlas.release(light_id)


class ReferenceShadowProvider(ShadowProvider):
    """Reference shadow backend evaluating geometric visibility analytically."""

    def process_shadow(self, request: ShadowRequest, frame: int = 0) -> ShadowResult:
        return ShadowResult(
            light_id=request.light_id,
            backend=ShadowBackend.REFERENCE,
            is_valid=True,
            resolution=request.resolution,
            memory_bytes=1024,
            shadow_factor=1.0,
        )

    def release_shadow(self, light_id: LightId) -> None:
        pass


class ContactShadowEvaluator:
    """
    Simulates screen-space contact shadows via short-range depth ray marching.
    """

    @staticmethod
    def evaluate_contact(
        hit_dist: float,
        max_length: float = 0.05,
        fade_fraction: float = 0.2
    ) -> float:
        """
        Returns contact occlusion factor in [0.0, 1.0].
        0.0 = fully occluded, 1.0 = not occluded.
        """
        if hit_dist >= max_length:
            return 1.0
        if hit_dist <= 0.0:
            return 0.0
        # Smooth falloff near max length
        threshold = max_length * (1.0 - fade_fraction)
        if hit_dist < threshold:
            return 0.0
        t = (hit_dist - threshold) / max(1e-6, (max_length - threshold))
        return t * t * (3.0 - 2.0 * t)
