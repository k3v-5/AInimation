# Remediation Design Report: Camera Look-At, Lumen Lighting Constraints & MRQ Cancellation

**Agent**: `explorer_m2_it2_3`  
**Role**: `explorer` (Read-only Investigation & Synthesis)  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m2_it2_3`  
**Parent Task ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Date**: 2026-10-14  
**Target Files**:
- `backend/ue5/camera.py`
- `backend/ue5/lighting.py`
- `backend/ue5/mrq.py`

---

## 1. Observation

### 1.1 CineCamera `front_close` Preset Target Tracking (`backend/ue5/camera.py`)
- **Direct Observation**:
  In `backend/ue5/camera.py`, lines 143–150:
  ```python
  elif preset == "front_close":
      x = 0.0 + 20.0 * math.sin(progress * math.pi * 4.0)
      y = -self.distance * 0.5
      z = center_z + 10.0 * math.cos(progress * math.pi * 2.0)
      pitch = 0.0
      yaw = 0.0
      fov = max(25.0, self.default_fov - 15.0)
  ```
- **Context & Defect**:
  The camera is positioned at $y = -\text{distance} \times 0.5$ (offset along the negative Y axis) with subtle sinusoidal displacement in X and Z. The focal target is at `target = Vector3D(x=0.0, y=0.0, z=center_z)`.
  In Unreal Engine's coordinate system (+X forward, +Y right, +Z up), pointing from $(0, -200, \text{center\_z})$ to $(0, 0, \text{center\_z})$ requires a yaw of $+90.0^\circ$ (pointing towards +Y).
  By hardcoding `pitch = 0.0, yaw = 0.0`, the camera is fixed pointing towards world +X (tangent to the target), causing the camera to look away from the focal actor instead of facing it. Other presets (`smooth_orbit`, `spiral_ascent`, `dramatic_orbit`) call `self.calculate_look_at(cam_pos, target)`.
  Additionally, line 69 defines `target = Vector3D(x=0.0, y=0.0, z=center_z)`. To satisfy the drop-in requirement `self.calculate_look_at(Vector3D(x=x, y=y, z=z), target_pos)`, `target_pos` should be defined as `target_pos = target`.

---

### 1.2 Lumen Lighting Rig Boundary Constraints & Null Safety (`backend/ue5/lighting.py`)
- **Direct Observation 1 (Intensity Boundary)**:
  In `backend/ue5/lighting.py`, lines 25–35:
  ```python
  class LightActorConfig(StrictBaseModel):
      """Configuration for an individual light actor in the UE5 scene."""
      name: str = Field(..., description="Unique actor name of the light")
      light_type: str = Field(..., description="Directional, Point, Spot, or Sky")
      intensity: float = Field(default=5000.0, description="Luminous flux in Lumens or illuminance in Lux")
  ```
  `intensity` lacks a `ge=0.0` boundary constraint. As noted by `challenger_m2_2` (Section 1.4, Finding 1), it allows non-physical negative intensities (e.g., `intensity = -5000.0`), violating photometric realism in Lumen lighting.
- **Direct Observation 2 (Null Safety on Preset)**:
  In `backend/ue5/lighting.py`, lines 52–57 and 217–221:
  ```python
  @classmethod
  def get_preset(cls, preset_name: str = "studio_3point") -> LumenLightingSetup:
      name = preset_name.lower().strip()
  ...
  def setup_lumen_lighting(preset: str = "studio_3point") -> LumenLightingSetup:
      return LightingRig.get_preset(preset)
  ```
  If `preset=None` is passed to `setup_lumen_lighting(None)` or `LightingRig.get_preset(None)`, line 57 raises:
  `AttributeError: 'NoneType' object has no attribute 'lower'`.
  It must safely default `preset is None` to `"studio_3point"`.

---

### 1.3 Movie Render Queue Synchronous Facade Cancellation (`backend/ue5/mrq.py`)
- **Direct Observation**:
  In `backend/ue5/mrq.py`, lines 103–108:
  ```python
  async def render_async(
      self,
      job_config: MovieRenderQueueJobConfig,
      cancellation_token: Optional[asyncio.Event] = None,
      duration_seconds: float = 3.0,
  ) -> RenderResult:
  ```
  `render_async()` fully implements cooperative cancellation checking `cancellation_token.is_set()` in both warmup and frame execution loops.
  However, in lines 193–245 and 247–266:
  ```python
  def render(
      self,
      scene_path: str,
      output_path: str,
      fps: int = 30,
      resolution: str = "1280x720",
      warmup_frames: int = 15,
      anti_aliasing_samples: int = 8,
  ) -> RenderResult:
  ...
  def render_sequence(
      scene_path: str,
      output_path: str,
      fps: int = 30,
      resolution: str = "1280x720",
      warmup_frames: int = 15,
      anti_aliasing_samples: int = 8,
  ) -> RenderResult:
  ```
  Neither `MRQManager.render()` nor `render_sequence()` exposes `cancellation_token`. Neither forwards it to `render_async()`.
  Consequently, callers using the synchronous API cannot cooperatively abort an in-flight render job.

---

## 2. Logic Chain

1. **Camera Look-At Logic**:
   - `calculate_look_at(cam_pos, target_pos)` calculates spherical angles `(pitch, yaw)` using `atan2(dy, dx)` for yaw and `atan2(dz, hypot(dx, dy))` for pitch.
   - For `front_close`, placing the camera at `Vector3D(x=x, y=y, z=z)` and targeting `target_pos = Vector3D(x=0.0, y=0.0, z=center_z)` produces a yaw facing towards the target ($+90^\circ$ nominal) and corrects for the periodic bobbing in X and Z.
   - Aliasing `target_pos = target` at the beginning of `generate_track()` ensures `target_pos` is in scope and eliminates any `NameError` risk while matching the exact specified replacement expression.

2. **Lighting Model & Null Safety Logic**:
   - Pydantic v2 `Field(..., ge=0.0)` enforces schema-level validation at instantiation time, rejecting negative photometric values before any downstream call to Unreal Engine Remote Control.
   - Using `preset_name: Optional[str] = "studio_3point"` and normalizing via `name = (preset_name or "studio_3point").lower().strip()` guarantees that `None`, empty string `""`, or whitespace-only inputs evaluate cleanly without throwing `AttributeError`.

3. **MRQ Cancellation Logic**:
   - By adding `cancellation_token: Optional[asyncio.Event] = None` to both `MRQManager.render()` and `render_sequence()`, synchronous callers can supply an `asyncio.Event`.
   - Forwarding `cancellation_token=cancellation_token` to `render_async(job_config, cancellation_token=cancellation_token)` ensures that if the event is set:
     - In the worker thread path, `_worker()` catches the resulting `asyncio.CancelledError` via `BaseException` handling and re-raises it to the synchronous caller.
     - In the direct `asyncio.run()` path, `asyncio.run` propagates `asyncio.CancelledError`.

---

## 3. Caveats

1. **AST Zero-Any Compliance**:
   All new and modified function signatures maintain 100% Zero-Any compliance (`Optional[asyncio.Event]`, `Optional[str]`, `Vector3D`). No `typing.Any` or unannotated variables are introduced.
2. **Backwards Compatibility**:
   - Adding `cancellation_token: Optional[asyncio.Event] = None` as a default keyword parameter maintains backwards compatibility with existing positional and keyword calls in `tests/backend/test_ue5_bridge.py`.
   - Adding `ge=0.0` to `LightActorConfig.intensity` does not affect existing tests because all valid light presets use intensities $\ge 500.0$.
3. **Execution Scope**:
   This agent operates strictly under read-only guidelines. The code modifications below are provided as validated drop-in replacement designs and unified git diffs for implementation by the designated worker agent.

---

## 4. Conclusion & Complete Drop-In Remediation Designs

### 4.1 Remediation 1: `backend/ue5/camera.py`

#### Summary of Changes:
1. In `CineCameraChoreographer.generate_track()`, define `target_pos = target` alongside `target = Vector3D(...)`.
2. In the `front_close` preset branch (lines 143–150), replace:
   ```python
   pitch = 0.0
   yaw = 0.0
   ```
   with:
   ```python
   pitch, yaw = self.calculate_look_at(Vector3D(x=x, y=y, z=z), target_pos)
   ```

#### Unified Diff Patch (`camera.patch`):
```diff
--- a/backend/ue5/camera.py
+++ b/backend/ue5/camera.py
@@ -67,6 +67,7 @@ class CineCameraChoreographer:
         duration = max(0.1, float(total_duration))
         keyframes: List[CameraKeyframe] = []
         target = Vector3D(x=0.0, y=0.0, z=center_z)
+        target_pos = target
 
         # Filter and sort beats within [0.0, duration]
         sorted_beats = sorted([b for b in beat_timestamps if 0.0 <= b <= duration])
@@ -144,8 +145,7 @@ class CineCameraChoreographer:
                 x = 0.0 + 20.0 * math.sin(progress * math.pi * 4.0)
                 y = -self.distance * 0.5
                 z = center_z + 10.0 * math.cos(progress * math.pi * 2.0)
-                pitch = 0.0
-                yaw = 0.0
+                pitch, yaw = self.calculate_look_at(Vector3D(x=x, y=y, z=z), target_pos)
                 fov = max(25.0, self.default_fov - 15.0)
 
             elif preset == "spiral_ascent":
```

#### Full Replacement Code for `backend/ue5/camera.py`:
```python
"""
CineCamera Choreographer for Unreal Engine 5.

Generates beat-synced cinematics and camera motion tracks aligned with audio
onset grids and music rhythm cues. Supports 5 cinematic presets:
smooth_orbit, dramatic_orbit, aerial_pan, front_close, and spiral_ascent.

100% Zero-Any compliant with Pydantic v2 strict models.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple, Union

from backend.core.models import CameraKeyframe, Vector3D


class CineCameraChoreographer:
    """
    Choreographs procedural CineCamera movements driven by musical beat timestamps.
    Provides mathematical Look-At tracking, physical FOV/distance clamping, and
    fallbacks for empty or out-of-bounds beat grids.
    """

    def __init__(self, default_fov: float = 45.0, distance: float = 400.0) -> None:
        self.default_fov: float = max(10.0, min(120.0, default_fov))
        self.distance: float = max(50.0, distance)

    @staticmethod
    def calculate_look_at(cam_pos: Vector3D, target_pos: Vector3D) -> Tuple[float, float]:
        """
        Compute camera Pitch and Yaw to face a 3D target point in Unreal coordinates.
        Unreal Engine coordinate system: X forward, Y right, Z up.

        Returns:
            Tuple of (pitch_degrees, yaw_degrees).
        """
        dx = target_pos.x - cam_pos.x
        dy = target_pos.y - cam_pos.y
        dz = target_pos.z - cam_pos.z
        dist_xy = math.hypot(dx, dy)

        yaw = math.degrees(math.atan2(dy, dx))
        pitch = math.degrees(math.atan2(dz, max(1e-5, dist_xy)))
        return round(pitch, 2), round(yaw, 2)

    def generate_track(
        self,
        beat_timestamps: List[float],
        total_duration: float,
        preset: str = "smooth_orbit",
        center_z: float = 120.0,
    ) -> List[CameraKeyframe]:
        """
        Generate camera keyframes synchronized to audio beats.

        Args:
            beat_timestamps: List of timestamp markers in seconds.
            total_duration: Total sequence duration in seconds.
            preset: Motion preset ('smooth_orbit', 'dramatic_orbit', 'aerial_pan', 'front_close', 'spiral_ascent').
            center_z: Focal tracking height in centimeters (Z-axis).

        Returns:
            List of strictly validated CameraKeyframe objects.
        """
        duration = max(0.1, float(total_duration))
        keyframes: List[CameraKeyframe] = []
        target = Vector3D(x=0.0, y=0.0, z=center_z)
        target_pos = target

        # Filter and sort beats within [0.0, duration]
        sorted_beats = sorted([b for b in beat_timestamps if 0.0 <= b <= duration])

        # Fallback if beat list is empty: create start and end boundary keyframes
        if not sorted_beats:
            cam_start = Vector3D(x=0.0, y=-self.distance, z=center_z)
            p_start, y_start = self.calculate_look_at(cam_start, target)
            keyframes.append(
                CameraKeyframe(
                    time=0.0,
                    x=cam_start.x,
                    y=cam_start.y,
                    z=cam_start.z,
                    pitch=p_start,
                    yaw=y_start,
                    roll=0.0,
                    fov=self.default_fov,
                    focal_length=35.0,
                    aperture=2.8,
                    focus_distance=self.distance,
                )
            )

            cam_end = Vector3D(x=self.distance * 0.5, y=-self.distance * 0.866, z=center_z + 20.0)
            p_end, y_end = self.calculate_look_at(cam_end, target)
            keyframes.append(
                CameraKeyframe(
                    time=round(duration, 4),
                    x=round(cam_end.x, 2),
                    y=round(cam_end.y, 2),
                    z=round(cam_end.z, 2),
                    pitch=p_end,
                    yaw=y_end,
                    roll=0.0,
                    fov=self.default_fov,
                    focal_length=35.0,
                    aperture=2.8,
                    focus_distance=round(math.hypot(cam_end.x, cam_end.y), 2),
                )
            )
            return keyframes

        # Ensure start keyframe at 0.0
        if sorted_beats[0] > 0.05:
            sorted_beats.insert(0, 0.0)
        # Ensure ending keyframe at total_duration
        if sorted_beats[-1] < duration - 0.05:
            sorted_beats.append(duration)

        for i, t in enumerate(sorted_beats):
            progress = t / duration if duration > 0 else 0.0

            if preset == "dramatic_orbit":
                angle = progress * 2.0 * math.pi
                radius = self.distance * (0.8 + 0.4 * math.sin(angle * 2.0))
                x = radius * math.sin(angle)
                y = -radius * math.cos(angle)
                z = center_z + 40.0 * math.sin(angle * 3.0)
                cam_pos = Vector3D(x=x, y=y, z=z)
                base_pitch, base_yaw = self.calculate_look_at(cam_pos, target)
                pitch = base_pitch + 8.0 * math.sin(angle * 2.0)
                yaw = (base_yaw + 360.0) % 360.0
                fov = self.default_fov + (5.0 if i % 2 == 0 else -5.0)

            elif preset == "aerial_pan":
                x = (progress - 0.5) * self.distance * 1.5
                y = -self.distance * 0.9
                z = center_z + 200.0 - 50.0 * progress
                pitch = -25.0
                yaw = 15.0 * math.sin(progress * math.pi)
                fov = self.default_fov + 10.0

            elif preset == "front_close":
                x = 0.0 + 20.0 * math.sin(progress * math.pi * 4.0)
                y = -self.distance * 0.5
                z = center_z + 10.0 * math.cos(progress * math.pi * 2.0)
                pitch, yaw = self.calculate_look_at(Vector3D(x=x, y=y, z=z), target_pos)
                fov = max(25.0, self.default_fov - 15.0)

            elif preset == "spiral_ascent":
                angle = progress * 3.0 * math.pi
                radius = self.distance * (1.0 - 0.2 * progress)
                x = radius * math.sin(angle)
                y = -radius * math.cos(angle)
                z = center_z - 30.0 + 150.0 * progress
                cam_pos = Vector3D(x=x, y=y, z=z)
                pitch, yaw = self.calculate_look_at(cam_pos, target)
                fov = self.default_fov

            else:  # Default 'smooth_orbit'
                angle = progress * math.pi * 1.5
                x = self.distance * math.sin(angle)
                y = -self.distance * math.cos(angle)
                z = center_z + 20.0 * math.sin(progress * math.pi)
                cam_pos = Vector3D(x=x, y=y, z=z)
                pitch, yaw = self.calculate_look_at(cam_pos, target)
                fov = self.default_fov

            # Compute physical focus distance to center target
            focus_dist = round(math.sqrt(x * x + y * y + (z - center_z) ** 2), 2)
            focal_len = round(36.0 / (2.0 * math.tan(math.radians(max(10.0, min(120.0, fov)) / 2.0))), 1)

            kf = CameraKeyframe(
                time=round(t, 4),
                x=round(x, 2),
                y=round(y, 2),
                z=round(z, 2),
                pitch=round(pitch, 2),
                yaw=round(yaw, 2),
                roll=0.0,
                fov=round(max(10.0, min(120.0, fov)), 1),
                focal_length=focal_len,
                aperture=2.8,
                focus_distance=max(50.0, focus_dist),
            )
            keyframes.append(kf)

        return keyframes


def generate_camera_track(
    beat_timestamps: List[float],
    total_duration: float,
    preset: str = "smooth_orbit",
    default_fov: float = 45.0,
    distance: float = 400.0,
) -> List[CameraKeyframe]:
    """
    Functional facade for generating a CineCamera choreography track.
    """
    choreographer = CineCameraChoreographer(default_fov=default_fov, distance=distance)
    return choreographer.generate_track(
        beat_timestamps=beat_timestamps,
        total_duration=total_duration,
        preset=preset,
    )
```

---

### 4.2 Remediation 2: `backend/ue5/lighting.py`

#### Summary of Changes:
1. In `LightActorConfig`, add boundary constraint `intensity: float = Field(default=5000.0, ge=0.0, ...)`.
2. In `LightingRig.get_preset()`, update signature to `preset_name: Optional[str] = "studio_3point"` and normalize `name = (preset_name or "studio_3point").lower().strip()`.
3. In `setup_lumen_lighting()`, update signature to `preset: Optional[str] = "studio_3point"` and delegate to `LightingRig.get_preset(preset or "studio_3point")`.

#### Unified Diff Patch (`lighting.patch`):
```diff
--- a/backend/ue5/lighting.py
+++ b/backend/ue5/lighting.py
@@ -26,7 +26,7 @@ class LightActorConfig(StrictBaseModel):
     """Configuration for an individual light actor in the UE5 scene."""
     name: str = Field(..., description="Unique actor name of the light")
     light_type: str = Field(..., description="Directional, Point, Spot, or Sky")
-    intensity: float = Field(default=5000.0, description="Luminous flux in Lumens or illuminance in Lux")
+    intensity: float = Field(default=5000.0, ge=0.0, description="Luminous flux in Lumens or illuminance in Lux")
     color: ColorRGB = Field(default_factory=lambda: ColorRGB(r=1.0, g=1.0, b=1.0))
     position: Vector3D = Field(default_factory=Vector3D)
     rotation: Rotator3D = Field(default_factory=Rotator3D)
@@ -49,12 +49,12 @@ class LightingRig:
     """
 
     @classmethod
-    def get_preset(cls, preset_name: str = "studio_3point") -> LumenLightingSetup:
+    def get_preset(cls, preset_name: Optional[str] = "studio_3point") -> LumenLightingSetup:
         """
         Build a Lumen-enabled lighting setup based on a preset name.
         Falls back safely to 'studio_3point' if the preset is unknown.
         """
-        name = preset_name.lower().strip()
+        name = (preset_name or "studio_3point").lower().strip()
 
         if "cyberpunk" in name or "neon" in name:
             lights = [
@@ -214,9 +214,9 @@ class LightingRig:
         )
 
 
-def setup_lumen_lighting(preset: str = "studio_3point") -> LumenLightingSetup:
+def setup_lumen_lighting(preset: Optional[str] = "studio_3point") -> LumenLightingSetup:
     """
     Functional helper to configure a Lumen lighting rig.
+    Safely defaults to 'studio_3point' if preset is None.
     """
-    return LightingRig.get_preset(preset)
+    return LightingRig.get_preset(preset or "studio_3point")
```

#### Full Replacement Code for `backend/ue5/lighting.py`:
```python
"""
Lumen Lighting Rig Configuration for Unreal Engine 5.

Configures dynamic real-time global illumination presets adhering to Lumen standards.
Supports 5 lighting rig presets:
- studio_3point: Balanced 3-point key/fill/rim with ambient skylight.
- cyberpunk_neon: High-energy stylized neon palette (cyan, magenta, amber).
- dramatic: Chiaroscuro high-contrast lighting with strong rim separation.
- outdoor_sunlight: High-lux directional sun (75,000 lux) and atmospheric sky.
- night_moonlight: Cool moonlight (1,500 lux, 8500K) and subtle nocturnal fill.

100% Zero-Any compliant with Pydantic v2 strict models.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from backend.core.models import ColorRGB, Rotator3D, StrictBaseModel, Vector3D
from pydantic import Field

logger = logging.getLogger("ianimation.ue5.lighting")


class LightActorConfig(StrictBaseModel):
    """Configuration for an individual light actor in the UE5 scene."""
    name: str = Field(..., description="Unique actor name of the light")
    light_type: str = Field(..., description="Directional, Point, Spot, or Sky")
    intensity: float = Field(default=5000.0, ge=0.0, description="Luminous flux in Lumens or illuminance in Lux")
    color: ColorRGB = Field(default_factory=lambda: ColorRGB(r=1.0, g=1.0, b=1.0))
    position: Vector3D = Field(default_factory=Vector3D)
    rotation: Rotator3D = Field(default_factory=Rotator3D)
    cast_shadows: bool = Field(default=True)
    temperature_kelvin: Optional[float] = Field(default=None)


class LumenLightingSetup(StrictBaseModel):
    """Collection of light actors and global Lumen post-process volume parameters."""
    preset_name: str
    lights: List[LightActorConfig]
    indirect_lighting_intensity: float = Field(default=1.2)
    lumen_global_illumination: bool = Field(default=True)
    lumen_reflections: bool = Field(default=True)


class LightingRig:
    """
    Manages and synthesizes Lumen-enabled architectural and cinematographic lighting rigs.
    """

    @classmethod
    def get_preset(cls, preset_name: Optional[str] = "studio_3point") -> LumenLightingSetup:
        """
        Build a Lumen-enabled lighting setup based on a preset name.
        Falls back safely to 'studio_3point' if the preset is unknown.
        """
        name = (preset_name or "studio_3point").lower().strip()

        if "cyberpunk" in name or "neon" in name:
             lights = [
                LightActorConfig(
                    name="Key_NeonCyan",
                    light_type="Spot",
                    intensity=8000.0,
                    color=ColorRGB(r=0.0, g=0.9, b=1.0),
                    position=Vector3D(x=-200.0, y=-250.0, z=220.0),
                    rotation=Rotator3D(pitch=-25.0, yaw=45.0, roll=0.0),
                    temperature_kelvin=9000.0,
                ),
                LightActorConfig(
                    name="Fill_NeonMagenta",
                    light_type="Spot",
                    intensity=6000.0,
                    color=ColorRGB(r=1.0, g=0.0, b=0.8),
                    position=Vector3D(x=200.0, y=-250.0, z=180.0),
                    rotation=Rotator3D(pitch=-20.0, yaw=-45.0, roll=0.0),
                ),
                LightActorConfig(
                    name="Rim_NeonAmber",
                    light_type="Point",
                    intensity=12000.0,
                    color=ColorRGB(r=1.0, g=0.6, b=0.0),
                    position=Vector3D(x=0.0, y=250.0, z=260.0),
                ),
            ]
             actual_name = "cyberpunk_neon"

        elif "dramatic" in name or "chiaroscuro" in name:
            lights = [
                LightActorConfig(
                    name="Key_Chiaroscuro",
                    light_type="Spot",
                    intensity=15000.0,
                    color=ColorRGB(r=1.0, g=0.95, b=0.85),
                    position=Vector3D(x=-300.0, y=-200.0, z=300.0),
                    rotation=Rotator3D(pitch=-40.0, yaw=35.0, roll=0.0),
                    temperature_kelvin=4800.0,
                ),
                LightActorConfig(
                    name="Rim_HairLight",
                    light_type="Spot",
                    intensity=10000.0,
                    color=ColorRGB(r=0.7, g=0.8, b=1.0),
                    position=Vector3D(x=150.0, y=250.0, z=280.0),
                    rotation=Rotator3D(pitch=-30.0, yaw=-140.0, roll=0.0),
                    temperature_kelvin=7500.0,
                ),
            ]
            actual_name = "dramatic"

        elif "sunlight" in name or "outdoor" in name:
            lights = [
                LightActorConfig(
                    name="Directional_Sun",
                    light_type="Directional",
                    intensity=75000.0,
                    color=ColorRGB(r=1.0, g=0.96, b=0.9),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                    rotation=Rotator3D(pitch=-45.0, yaw=30.0, roll=0.0),
                    temperature_kelvin=5500.0,
                ),
                LightActorConfig(
                    name="Sky_AmbientDay",
                    light_type="Sky",
                    intensity=2500.0,
                    color=ColorRGB(r=0.75, g=0.85, b=1.0),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                ),
                LightActorConfig(
                    name="Fill_GroundBounce",
                    light_type="Spot",
                    intensity=3000.0,
                    color=ColorRGB(r=0.9, g=0.85, b=0.75),
                    position=Vector3D(x=0.0, y=-200.0, z=50.0),
                    rotation=Rotator3D(pitch=30.0, yaw=0.0, roll=0.0),
                ),
            ]
            actual_name = "outdoor_sunlight"

        elif "moon" in name or "night" in name or "nocturnal" in name:
            lights = [
                LightActorConfig(
                    name="Directional_Moon",
                    light_type="Directional",
                    intensity=1500.0,
                    color=ColorRGB(r=0.65, g=0.75, b=1.0),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                    rotation=Rotator3D(pitch=-60.0, yaw=120.0, roll=0.0),
                    temperature_kelvin=8500.0,
                ),
                LightActorConfig(
                    name="Sky_AmbientNight",
                    light_type="Sky",
                    intensity=500.0,
                    color=ColorRGB(r=0.2, g=0.3, b=0.6),
                    position=Vector3D(x=0.0, y=0.0, z=1000.0),
                ),
                LightActorConfig(
                    name="Rim_CoolBlue",
                    light_type="Point",
                    intensity=4000.0,
                    color=ColorRGB(r=0.4, g=0.7, b=1.0),
                    position=Vector3D(x=0.0, y=250.0, z=220.0),
                ),
            ]
            actual_name = "night_moonlight"

        else:
            # Default fallback: studio_3point
            if name != "studio_3point":
                logger.info("Unknown lighting preset '%s'; falling back to 'studio_3point'.", preset_name)
            lights = [
                LightActorConfig(
                    name="Key_Light",
                    light_type="Spot",
                    intensity=8000.0,
                    color=ColorRGB(r=1.0, g=0.98, b=0.95),
                    position=Vector3D(x=-250.0, y=-300.0, z=250.0),
                    rotation=Rotator3D(pitch=-30.0, yaw=40.0, roll=0.0),
                    temperature_kelvin=5200.0,
                ),
                LightActorConfig(
                    name="Fill_Light",
                    light_type="Spot",
                    intensity=3500.0,
                    color=ColorRGB(r=0.85, g=0.9, b=1.0),
                    position=Vector3D(x=250.0, y=-250.0, z=180.0),
                    rotation=Rotator3D(pitch=-20.0, yaw=-35.0, roll=0.0),
                    temperature_kelvin=6500.0,
                ),
                LightActorConfig(
                    name="Rim_Backlight",
                    light_type="Point",
                    intensity=5000.0,
                    color=ColorRGB(r=1.0, g=1.0, b=1.0),
                    position=Vector3D(x=0.0, y=300.0, z=280.0),
                ),
                LightActorConfig(
                    name="Sky_Ambient",
                    light_type="Sky",
                    intensity=1000.0,
                    color=ColorRGB(r=0.9, g=0.95, b=1.0),
                    position=Vector3D(x=0.0, y=0.0, z=500.0),
                ),
            ]
            actual_name = "studio_3point"

        return LumenLightingSetup(
            preset_name=actual_name,
            lights=lights,
            indirect_lighting_intensity=1.2,
            lumen_global_illumination=True,
            lumen_reflections=True,
        )


def setup_lumen_lighting(preset: Optional[str] = "studio_3point") -> LumenLightingSetup:
    """
    Functional helper to configure a Lumen lighting rig.
    Safely defaults to 'studio_3point' if preset is None.
    """
    return LightingRig.get_preset(preset or "studio_3point")
```

---

### 4.3 Remediation 3: `backend/ue5/mrq.py`

#### Summary of Changes:
1. In `MRQManager.render()`, add parameter `cancellation_token: Optional[asyncio.Event] = None`.
2. Forward `cancellation_token=cancellation_token` in `self.render_async(job_config, cancellation_token=cancellation_token)` inside both the threaded event-loop worker and the `asyncio.run()` fallback.
3. In `render_sequence()`, add parameter `cancellation_token: Optional[asyncio.Event] = None` and forward it to `manager.render(..., cancellation_token=cancellation_token)`.

#### Unified Diff Patch (`mrq.patch`):
```diff
--- a/backend/ue5/mrq.py
+++ b/backend/ue5/mrq.py
@@ -199,6 +199,7 @@ class MRQManager:
         resolution: str = "1280x720",
         warmup_frames: int = 15,
         anti_aliasing_samples: int = 8,
+        cancellation_token: Optional[asyncio.Event] = None,
     ) -> RenderResult:
         """
         Synchronous facade for MRQ rendering.
@@ -226,7 +227,9 @@ class MRQManager:
                 new_loop = asyncio.new_event_loop()
                 asyncio.set_event_loop(new_loop)
                 try:
-                    res = new_loop.run_until_complete(self.render_async(job_config))
+                    res = new_loop.run_until_complete(
+                        self.render_async(job_config, cancellation_token=cancellation_token)
+                    )
                     result_holder.append(res)
                 except BaseException as err:
                     exc_holder.append(err)
@@ -242,7 +245,9 @@ class MRQManager:
                 raise exc_holder[0]
             return result_holder[0]
         else:
-            return asyncio.run(self.render_async(job_config))
+            return asyncio.run(
+                self.render_async(job_config, cancellation_token=cancellation_token)
+            )
 
 
 def render_sequence(
@@ -252,6 +257,7 @@ def render_sequence(
     resolution: str = "1280x720",
     warmup_frames: int = 15,
     anti_aliasing_samples: int = 8,
+    cancellation_token: Optional[asyncio.Event] = None,
 ) -> RenderResult:
     """
     Functional facade for MRQ video rendering.
@@ -264,4 +270,5 @@ def render_sequence(
         resolution=resolution,
         warmup_frames=warmup_frames,
         anti_aliasing_samples=anti_aliasing_samples,
+        cancellation_token=cancellation_token,
     )
```

#### Full Replacement Code for `backend/ue5/mrq.py` (render methods):
```python
    def render(
        self,
        scene_path: str,
        output_path: str,
        fps: int = 30,
        resolution: str = "1280x720",
        warmup_frames: int = 15,
        anti_aliasing_samples: int = 8,
        cancellation_token: Optional[asyncio.Event] = None,
    ) -> RenderResult:
        """
        Synchronous facade for MRQ rendering.
        Supports cooperative cancellation via optional cancellation_token.
        """
        job_config = MovieRenderQueueJobConfig(
            scene_path=scene_path,
            output_path=output_path,
            fps=fps,
            resolution=resolution,
            warmup_frames=warmup_frames,
            anti_aliasing_samples=anti_aliasing_samples,
        )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None and loop.is_running():
            # If called inside an active event loop, run in a background worker thread
            result_holder: List[RenderResult] = []
            exc_holder: List[BaseException] = []

            def _worker() -> None:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    res = new_loop.run_until_complete(
                        self.render_async(job_config, cancellation_token=cancellation_token)
                    )
                    result_holder.append(res)
                except BaseException as err:
                    exc_holder.append(err)
                finally:
                    new_loop.close()

            import threading
            th = threading.Thread(target=_worker)
            th.start()
            th.join()

            if exc_holder:
                raise exc_holder[0]
            return result_holder[0]
        else:
            return asyncio.run(
                self.render_async(job_config, cancellation_token=cancellation_token)
            )


def render_sequence(
    scene_path: str,
    output_path: str,
    fps: int = 30,
    resolution: str = "1280x720",
    warmup_frames: int = 15,
    anti_aliasing_samples: int = 8,
    cancellation_token: Optional[asyncio.Event] = None,
) -> RenderResult:
    """
    Functional facade for MRQ video rendering.
    Supports cooperative cancellation via optional cancellation_token.
    """
    manager = MRQManager()
    return manager.render(
        scene_path=scene_path,
        output_path=output_path,
        fps=fps,
        resolution=resolution,
        warmup_frames=warmup_frames,
        anti_aliasing_samples=anti_aliasing_samples,
        cancellation_token=cancellation_token,
    )
```

---

## 5. Verification Method

Once the patches are applied by the worker agent, verify independently with the following procedures:

### 5.1 Automated Test Execution
Run the full existing test suite to ensure zero regressions:
```powershell
python -m pytest tests/backend/test_ue5_bridge.py -v
```
*Expected*: All 43 bridge tests pass cleanly.

### 5.2 Verification of CineCamera `front_close` Preset
Execute the following verification script:
```powershell
python -c "
from backend.ue5.camera import generate_camera_track

track = generate_camera_track(beat_timestamps=[0.5, 1.0, 1.5], total_duration=2.0, preset='front_close')
assert len(track) >= 3
for kf in track:
    # Camera is in front along -Y; target is at (0, 0, 120); yaw facing +Y must be approximately 90 degrees
    assert 70.0 <= kf.yaw <= 110.0, f'Unexpected yaw: {kf.yaw}'
    assert abs(kf.pitch) < 30.0, f'Unexpected pitch: {kf.pitch}'
print('PASS: front_close preset dynamically tracks target with yaw ~ 90.0 degrees')
"
```

### 5.3 Verification of Lumen Lighting Null Safety and Negative Intensity Rejection
```powershell
python -c "
import pytest
from pydantic import ValidationError
from backend.ue5.lighting import LightActorConfig, setup_lumen_lighting, LightingRig

# 1. Null safety check
s1 = setup_lumen_lighting(None)
assert s1.preset_name == 'studio_3point'
s2 = LightingRig.get_preset(None)
assert s2.preset_name == 'studio_3point'
print('PASS: setup_lumen_lighting(None) defaults cleanly to studio_3point')

# 2. Intensity constraint check
try:
    LightActorConfig(name='Neg', light_type='Spot', intensity=-100.0)
    raise AssertionError('Negative intensity should have failed validation!')
except ValidationError:
    print('PASS: negative intensity correctly rejected by Field(ge=0.0)')
"
```

### 5.4 Verification of MRQ Synchronous Facade Cancellation
```powershell
python -c "
import asyncio
from pathlib import Path
from backend.ue5.mrq import MRQManager, render_sequence

token = asyncio.Event()
token.set()  # Pre-cancelled token

manager = MRQManager(output_dir=Path('./renders'))
try:
    manager.render(
        scene_path='/Game/TestScene',
        output_path='./renders/test_cancel.mp4',
        cancellation_token=token
    )
    raise AssertionError('Render did not raise CancelledError!')
except asyncio.CancelledError:
    print('PASS: MRQManager.render() successfully aborted via cancellation_token')

try:
    render_sequence(
        scene_path='/Game/TestScene',
        output_path='./renders/test_cancel2.mp4',
        cancellation_token=token
    )
    raise AssertionError('render_sequence did not raise CancelledError!')
except asyncio.CancelledError:
    print('PASS: render_sequence() successfully aborted via cancellation_token')
"
```

### 5.5 AST Zero-Any Policy Verification
```powershell
python -c "
import ast
from pathlib import Path

files = [
    Path('backend/ue5/camera.py'),
    Path('backend/ue5/lighting.py'),
    Path('backend/ue5/mrq.py'),
]

for p in files:
    tree = ast.parse(p.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == 'Any':
            raise AssertionError(f'Zero-Any violation in {p}')
        if isinstance(node, ast.ImportFrom) and any(alias.name == 'Any' for alias in node.names):
            raise AssertionError(f'Zero-Any import violation in {p}')

print('PASS: 100% Zero-Any compliant across camera.py, lighting.py, mrq.py')
"
```
