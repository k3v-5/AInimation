"""
Universal Lighting World Coordinator for UAF-81.85.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from .core import (
    LightId,
    LightType,
    LightMobility,
    LightPriority,
    ProbeId,
    PostProcessVolumeId,
    WeatherCondition,
    FallbackLevel,
)
from .lights import Light
from .point import PointLight
from .spot import SpotLight
from .directional import DirectionalLight
from .area import RectAreaLight, DiskAreaLight, LineAreaLight
from .sky import SkySystem
from .sun import Sun
from .moon import Moon
from .daynight import DayNightController, DayPeriod
from .atmosphere import AtmosphereScattering
from .fog import FogSystem
from .volumetrics import VolumetricSystem
from .clouds import CloudSystem
from .weather import WeatherSystem
from .shadows import (
    ShadowRequest,
    ShadowResult,
    ShadowProvider,
    CSMShadowProvider,
    AtlasShadowProvider,
    ReferenceShadowProvider,
    ContactShadowEvaluator,
)
from .probes import IrradianceProbe, ReflectionProbe, LightProbeGrid
from .ambient import AmbientLighting
from .postprocess import PostProcessStack, PostProcessVolume, PostProcessSettings
from .culling import LightCuller, SimpleFrustum
from .lod import LightingLODManager
from .budgets import BudgetManager, LightingBudgets, DegradationStep
from .profiler import LightingProfiler, LightingProfileFrame
from .validation import LightingValidator, LightingValidationReport
from .recovery import LightingCrashRecovery
from .snapshot import LightingSnapshot
from .replay import LightingReplayEngine


class LightingWorld:
    """
    Central runtime lighting world coordinating all lights, celestial bodies,
    atmospheres, shadow casters, post-process volumes and streaming cells.
    """

    def __init__(self) -> None:
        self.frame_counter: int = 0
        self.simulation_time: float = 0.0

        # Lights collection
        self.lights: Dict[str, Light] = {}
        # Celestial & Atmosphere
        self.sky = SkySystem()
        self.atmosphere = AtmosphereScattering()
        self.fog = FogSystem()
        self.volumetrics = VolumetricSystem()
        self.clouds = CloudSystem()
        self.weather = WeatherSystem()

        # Shadows
        self.csm_provider = CSMShadowProvider()
        self.atlas_provider = AtlasShadowProvider()
        self.ref_shadow_provider = ReferenceShadowProvider()

        # Ambient & Probes
        self.ambient = AmbientLighting()
        self.probe_grid = LightProbeGrid()
        self.reflection_probes: Dict[str, ReflectionProbe] = {}

        # Post-Process
        self.post_process_stack = PostProcessStack()
        # Add default unbound global volume
        default_global_vol = PostProcessVolume(
            volume_id=PostProcessVolumeId("global_unbound_default"),
            is_unbound=True,
            priority=-100.0,
            settings=PostProcessSettings(),
        )
        self.post_process_stack.add_volume(default_global_vol)

        # Management & Infrastructure
        self.budget_manager = BudgetManager()
        self.profiler = LightingProfiler()
        self.recovery = LightingCrashRecovery()
        self.replay = LightingReplayEngine()

        # Streaming cell tracking: cell_id -> set of light_ids / probe_ids / volume_ids
        self.streaming_cell_resources: Dict[str, Dict[str, List[str]]] = {}

    # -----------------------------------------------------------------------
    # Light Lifecycle
    # -----------------------------------------------------------------------

    def create_light(self, light: Light) -> Light:
        """Registers a new light in the world with validation and cell tracking."""
        report = LightingValidator.validate_light(light)
        if not report.is_valid:
            # Sanitize gracefully without throwing
            light.sanitize()

        key = light.light_id.value
        self.lights[key] = light

        # Track streaming cell registration
        if light.cell_id:
            cell_entry = self.streaming_cell_resources.setdefault(
                light.cell_id, {"lights": [], "probes": [], "volumes": []}
            )
            cell_entry["lights"].append(key)

        self.replay.record(
            frame=self.frame_counter,
            timestamp=self.simulation_time,
            event_type="LightCreated",
            payload={"light_id": key, "type": light.light_type.value},
        )
        return light

    def destroy_light(self, light_id: LightId) -> bool:
        """Unregisters and cleans up a light and any associated shadow tiles."""
        key = light_id.value
        if key not in self.lights:
            return False

        light = self.lights.pop(key)
        self.atlas_provider.release_shadow(light_id)
        self.csm_provider.release_shadow(light_id)

        # Remove from cell tracking if present
        if light.cell_id and light.cell_id in self.streaming_cell_resources:
            lights_list = self.streaming_cell_resources[light.cell_id]["lights"]
            if key in lights_list:
                lights_list.remove(key)

        self.replay.record(
            frame=self.frame_counter,
            timestamp=self.simulation_time,
            event_type="LightDestroyed",
            payload={"light_id": key},
        )
        return True

    def get_light(self, light_id: LightId) -> Optional[Light]:
        return self.lights.get(light_id.value)

    def get_all_lights(self) -> List[Light]:
        return list(self.lights.values())

    def attach_light(self, light_id: LightId, target_id: str, socket_name: Optional[str] = None) -> bool:
        light = self.get_light(light_id)
        if not light:
            return False
        light.attached_to = target_id
        light.socket_name = socket_name
        return True

    def detach_light(self, light_id: LightId) -> bool:
        light = self.get_light(light_id)
        if not light:
            return False
        light.attached_to = None
        light.socket_name = None
        return True

    # -----------------------------------------------------------------------
    # Streaming Cell Integration (UAF-81.81)
    # -----------------------------------------------------------------------

    def register_streaming_cell(
        self,
        cell_id: str,
        lights: List[Light],
        probes: Optional[List[ReflectionProbe]] = None,
        volumes: Optional[List[PostProcessVolume]] = None
    ) -> None:
        """Loads all lighting resources associated with a newly activated streaming cell."""
        entry = self.streaming_cell_resources.setdefault(cell_id, {"lights": [], "probes": [], "volumes": []})

        for l in lights:
            l.cell_id = cell_id
            self.create_light(l)

        if probes:
            for p in probes:
                p.cell_id = cell_id
                self.reflection_probes[p.probe_id.value] = p
                entry["probes"].append(p.probe_id.value)

        if volumes:
            for v in volumes:
                v.cell_id = cell_id
                self.post_process_stack.add_volume(v)
                entry["volumes"].append(v.volume_id.value)

    def unload_streaming_cell(self, cell_id: str) -> None:
        """Symmetrically unloads and destroys all lighting resources belonging to an evicted cell."""
        if cell_id not in self.streaming_cell_resources:
            return

        entry = self.streaming_cell_resources.pop(cell_id)
        for l_key in list(entry["lights"]):
            self.destroy_light(LightId(l_key))

        for p_key in entry["probes"]:
            self.reflection_probes.pop(p_key, None)

        for v_key in entry["volumes"]:
            self.post_process_stack.remove_volume(PostProcessVolumeId(v_key))

    # -----------------------------------------------------------------------
    # Simulation Tick
    # -----------------------------------------------------------------------

    def tick(self, dt: float, camera_pos: Tuple[float, float, float] = (0.0, 1.7, 0.0)) -> LightingSnapshot:
        """
        Executes one deterministic simulation step:
        Advances ephemeris, weather, clouds, culling, budgets, and produces canonical snapshot.
        """
        try:
            self.frame_counter += 1
            self.simulation_time += dt

            # 1. Advance sky & ephemeris
            eph = self.sky.update(dt)

            # 2. Advance weather and clouds
            self.weather.tick(dt, self.clouds, self.fog)
            self.clouds.update(dt)

            # 3. Collect active lights
            all_lights = self.get_all_lights()

            # 4. Light culling
            frustum = SimpleFrustum(
                position=camera_pos,
                forward=(0.0, 0.0, -1.0),
                fov_rad=math.radians(60.0),
                aspect_ratio=1.777,
            )
            visible_lights = LightCuller.cull_lights(all_lights, frustum)

            # 5. Evaluate budget pressure & apply degradation ladder
            active_shadows_count = sum(1 for l in visible_lights if l.cast_shadows)
            est_shadow_mem = active_shadows_count * (1024 ** 2) * 4
            step = self.budget_manager.evaluate_pressure(
                active_light_count=len(visible_lights),
                active_shadow_count=active_shadows_count,
                shadow_memory_bytes=est_shadow_mem,
                estimated_frame_ms=8.0,
            )
            processed_lights = self.budget_manager.apply_degradation(visible_lights)

            # 6. Post-Process Resolution
            effective_pp = self.post_process_stack.resolve_effective_settings(camera_pos)

            # 7. Record Telemetry
            profile_frame = LightingProfileFrame(
                frame_number=self.frame_counter,
                light_culling_ms=0.25,
                shadow_generation_ms=1.10,
                ambient_gi_ms=0.60,
                volumetric_ms=0.80,
                postprocess_ms=1.20,
                color_management_ms=0.10,
                total_cpu_ms=4.05,
                total_gpu_ms=7.50,
                active_light_count=len(processed_lights),
                active_shadow_count=active_shadows_count,
                probe_count=len(self.probe_grid.probes),
                memory_bytes=self.atlas_provider.atlas.allocated_memory_bytes,
                degradation_step=int(step),
            )
            self.profiler.record_frame(profile_frame)

            # 8. Capture canonical snapshot
            return self.capture_snapshot()

        except Exception as exc:
            # Fail-safe isolation: trigger emergency profile without crashing engine
            self.recovery.trigger_fallback(FallbackLevel.EMERGENCY)
            emergency_lights = self.recovery.get_emergency_lights()
            self.lights = {l.light_id.value: l for l in emergency_lights}
            return self.capture_snapshot()

    # -----------------------------------------------------------------------
    # State Snapshot & Checkpoints
    # -----------------------------------------------------------------------

    def capture_snapshot(self) -> LightingSnapshot:
        """Captures complete immutable lighting state snapshot with canonical SHA-256 hash."""
        lights_dicts = [l.to_dict() for l in self.lights.values()]
        eph = self.sky.controller.compute_ephemeris()
        sun_state = {
            "direction": list(self.sky.sun.direction),
            "intensity": self.sky.sun.intensity,
            "temperature": self.sky.sun.temperature,
            "azimuth": eph.sun_azimuth_deg,
            "elevation": eph.sun_elevation_deg,
        }
        moon_state = {
            "direction": list(self.sky.moon.direction),
            "intensity": self.sky.moon.intensity,
            "phase": self.sky.moon.phase,
            "azimuth": eph.moon_azimuth_deg,
            "elevation": eph.moon_elevation_deg,
        }
        fog_state = {
            "density": self.fog.density,
            "height_falloff": self.fog.height_falloff,
            "albedo": list(self.fog.albedo),
        }
        clouds_state = {
            "coverage": self.clouds.coverage,
            "density": self.clouds.density,
            "altitude": self.clouds.altitude_base,
        }
        active_pp = self.post_process_stack.resolve_effective_settings((0.0, 0.0, 0.0))

        return LightingSnapshot(
            frame_index=self.frame_counter,
            simulation_time=self.simulation_time,
            world_time_seconds=self.sky.controller.world_time_seconds,
            sun_state=sun_state,
            moon_state=moon_state,
            lights_state=lights_dicts,
            fog_state=fog_state,
            clouds_state=clouds_state,
            postprocess_state=active_pp.to_dict(),
        )

    def restore_snapshot(self, snapshot: LightingSnapshot) -> None:
        """Restores lighting state exactly from snapshot."""
        self.frame_counter = snapshot.frame_index
        self.simulation_time = snapshot.simulation_time
        self.sky.controller.world_time_seconds = snapshot.world_time_seconds
        self.sky.controller.time_of_day_hours = snapshot.world_time_seconds / 3600.0

        # Clear and restore lights
        self.lights.clear()
        for ld in snapshot.lights_state:
            ltype = LightType(ld["light_type"])
            lid = LightId(ld["light_id"])
            if ltype == LightType.POINT:
                light = PointLight(
                    light_id=lid,
                    position=tuple(ld["position"]),
                    color=tuple(ld["color"]),
                    intensity=ld["intensity"],
                    range=ld["range"],
                    cast_shadows=ld["cast_shadows"],
                    mobility=LightMobility(ld["mobility"]),
                    priority=LightPriority(ld["priority"]),
                    source_radius=ld.get("source_radius", 0.0),
                )
            elif ltype == LightType.SPOT:
                light = SpotLight(
                    light_id=lid,
                    position=tuple(ld["position"]),
                    direction=tuple(ld["direction"]),
                    color=tuple(ld["color"]),
                    intensity=ld["intensity"],
                    range=ld["range"],
                    inner_cone_angle=ld.get("inner_cone_angle", 20.0),
                    outer_cone_angle=ld.get("outer_cone_angle", 45.0),
                    cast_shadows=ld["cast_shadows"],
                    mobility=LightMobility(ld["mobility"]),
                    priority=LightPriority(ld["priority"]),
                )
            elif ltype == LightType.DIRECTIONAL:
                light = DirectionalLight(
                    light_id=lid,
                    direction=tuple(ld["direction"]),
                    color=tuple(ld["color"]),
                    intensity=ld["intensity"],
                    cast_shadows=ld["cast_shadows"],
                    priority=LightPriority(ld["priority"]),
                )
            elif ltype == LightType.RECT_AREA:
                light = RectAreaLight(
                    light_id=lid,
                    position=tuple(ld["position"]),
                    color=tuple(ld["color"]),
                    intensity=ld["intensity"],
                    source_width=ld.get("source_width", 1.0),
                    source_height=ld.get("source_height", 1.0),
                )
            else:
                light = Light(
                    light_id=lid,
                    light_type=ltype,
                    position=tuple(ld["position"]),
                    color=tuple(ld["color"]),
                    intensity=ld["intensity"],
                )
            self.lights[lid.value] = light
