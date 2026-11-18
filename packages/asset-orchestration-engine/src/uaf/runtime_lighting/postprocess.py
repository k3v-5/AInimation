"""
Post-Process Stack, Volumes & Volume Blending for UAF-81.85.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .core import PostProcessVolumeId, ToneMapperType, ensure_finite_scalar, ensure_finite_vec3
from .exposure import ExposureSettings
from .color import ColorGradingSettings
from .bloom import BloomSettings
from .ao import AOSettings
from .dof import DOFSettings
from .motion_blur import MotionBlurSettings
from .lens import LensSettings


@dataclass
class PostProcessSettings:
    """
    Comprehensive collection of post-process parameters.
    """
    exposure: ExposureSettings = field(default_factory=ExposureSettings)
    tonemapper_type: ToneMapperType = ToneMapperType.ACES
    color_grading: ColorGradingSettings = field(default_factory=ColorGradingSettings)
    bloom: BloomSettings = field(default_factory=BloomSettings)
    ao: AOSettings = field(default_factory=AOSettings)
    dof: DOFSettings = field(default_factory=DOFSettings)
    motion_blur: MotionBlurSettings = field(default_factory=MotionBlurSettings)
    lens: LensSettings = field(default_factory=LensSettings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exposure_mode": self.exposure.mode.value,
            "fixed_ev100": self.exposure.fixed_ev100,
            "min_ev100": self.exposure.min_ev100,
            "max_ev100": self.exposure.max_ev100,
            "tonemapper": self.tonemapper_type.value,
            "saturation": self.color_grading.saturation,
            "contrast": self.color_grading.contrast,
            "gamma": self.color_grading.gamma,
            "bloom_enabled": self.bloom.enabled,
            "bloom_intensity": self.bloom.intensity,
            "ao_enabled": self.ao.enabled,
            "ao_intensity": self.ao.intensity,
            "dof_enabled": self.dof.enabled,
            "dof_focus_distance": self.dof.focus_distance,
            "motion_blur_enabled": self.motion_blur.enabled,
            "vignette_intensity": self.lens.vignette_intensity,
        }

    def compute_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class PostProcessVolume:
    """
    Spatial volume applying post-process overrides with priority and distance blending.
    """
    volume_id: PostProcessVolumeId
    is_unbound: bool = False
    priority: float = 0.0
    blend_weight: float = 1.0
    blend_radius: float = 5.0
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    extents: Tuple[float, float, float] = (10.0, 10.0, 10.0)  # Box half-extents
    settings: PostProcessSettings = field(default_factory=PostProcessSettings)
    cell_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.priority = ensure_finite_scalar(self.priority, "priority", 0.0)
        self.blend_weight = max(0.0, min(1.0, ensure_finite_scalar(self.blend_weight, "blend_weight", 1.0)))
        self.blend_radius = max(0.001, ensure_finite_scalar(self.blend_radius, "blend_radius", 5.0))
        self.position = ensure_finite_vec3(self.position, "position")
        self.extents = ensure_finite_vec3(self.extents, "extents", (10.0, 10.0, 10.0))

    def evaluate_weight(self, camera_pos: Tuple[float, float, float]) -> float:
        """Computes effective weight at camera position taking into account blend_radius."""
        if self.is_unbound:
            return self.blend_weight

        # Distance from point to box surface
        dx = max(0.0, abs(camera_pos[0] - self.position[0]) - self.extents[0])
        dy = max(0.0, abs(camera_pos[1] - self.position[1]) - self.extents[1])
        dz = max(0.0, abs(camera_pos[2] - self.position[2]) - self.extents[2])
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist == 0.0:
            return self.blend_weight
        elif dist >= self.blend_radius:
            return 0.0
        else:
            # Linear falloff over blend_radius
            t = 1.0 - (dist / self.blend_radius)
            return self.blend_weight * (t * t * (3.0 - 2.0 * t))


class PostProcessStack:
    """
    Manages active post-process volumes and resolves blended camera settings.
    """

    def __init__(self) -> None:
        self.volumes: Dict[str, PostProcessVolume] = {}

    def add_volume(self, volume: PostProcessVolume) -> None:
        self.volumes[volume.volume_id.value] = volume

    def remove_volume(self, volume_id: PostProcessVolumeId) -> None:
        self.volumes.pop(volume_id.value, None)

    def resolve_effective_settings(
        self,
        camera_pos: Tuple[float, float, float]
    ) -> PostProcessSettings:
        """
        Sorts active volumes by priority and blends settings smoothly.
        """
        if not self.volumes:
            return PostProcessSettings()

        # Collect volumes with weight > 0
        active_list: List[Tuple[float, float, PostProcessVolume]] = []
        for vol in self.volumes.values():
            w = vol.evaluate_weight(camera_pos)
            if w > 0.0:
                active_list.append((vol.priority, w, vol))

        if not active_list:
            return PostProcessSettings()

        # Sort by priority ascending so higher priority overrides
        active_list.sort(key=lambda x: x[0])

        base = PostProcessSettings()
        for _, weight, vol in active_list:
            v_set = vol.settings
            w = weight
            # Blend simple scalar attributes
            base.color_grading.saturation = base.color_grading.saturation * (1.0 - w) + v_set.color_grading.saturation * w
            base.color_grading.contrast = base.color_grading.contrast * (1.0 - w) + v_set.color_grading.contrast * w
            base.bloom.intensity = base.bloom.intensity * (1.0 - w) + v_set.bloom.intensity * w
            base.ao.intensity = base.ao.intensity * (1.0 - w) + v_set.ao.intensity * w
            base.lens.vignette_intensity = base.lens.vignette_intensity * (1.0 - w) + v_set.lens.vignette_intensity * w

            # For discrete/strong properties, higher priority wins if w > 0.5
            if w >= 0.5:
                base.tonemapper_type = v_set.tonemapper_type
                base.exposure.mode = v_set.exposure.mode
                base.dof.enabled = v_set.dof.enabled
                base.dof.focus_distance = v_set.dof.focus_distance
                base.bloom.enabled = v_set.bloom.enabled
                base.ao.enabled = v_set.ao.enabled

        return base
