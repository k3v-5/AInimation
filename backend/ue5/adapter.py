"""
Unreal Engine 5 Adapter conforming to Base3DEngineAdapter.

Decouples UE5 scene building and Movie Render Queue (MRQ) execution
following Clean Architecture and SOLID principles.
"""

from __future__ import annotations

from typing import List, Optional, Union

from backend.core.models import RenderResult, SceneBuildResult, SceneConfig
from backend.engines.base import Base3DEngineAdapter
from backend.ue5.client import UE5RestClient
from backend.ue5.lighting import LightingRig
from backend.ue5.mrq import render_sequence


class UE5Adapter(Base3DEngineAdapter):
    """
    Adapter for Unreal Engine 5 via Remote Control REST API and Movie Render Queue.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 30010) -> None:
        super().__init__(engine_name="ue5")
        self.client: UE5RestClient = UE5RestClient(host=host, port=port)

    def health_check(self) -> bool:
        """Check whether UE5 Remote Control REST endpoint is responsive."""
        return self.client.health_check()

    def build_scene(self, scene_config: SceneConfig) -> SceneBuildResult:
        """Assemble an Unreal Engine 5 cinematic Level Sequence."""
        actor_ids: List[str] = []

        # 1. Spawn character mesh actor
        char_id = self.client.spawn_actor(actor_class="SkeletalMeshActor")
        actor_ids.append(char_id)

        # 2. Spawn camera actor
        cam_id = self.client.spawn_actor(actor_class="CineCameraActor")
        actor_ids.append(cam_id)

        # 3. Configure Lumen lighting preset
        lighting_setup = LightingRig.get_preset(scene_config.lighting_preset)
        for light in lighting_setup.lights:
            light_id = self.client.spawn_actor(actor_class=f"{light.light_type}Light")
            actor_ids.append(light_id)

        scene_path = f"/Game/Sequences/LS_{scene_config.level_name}"
        return SceneBuildResult(
            success=True,
            actor_ids=actor_ids,
            scene_path=scene_path,
            camera_actor_id=cam_id,
            character_actor_id=char_id,
            message="UE5 scene built successfully with Lumen lighting and CineCamera track",
        )

    def render_video(
        self,
        scene_path: str,
        output_path: str,
        fps: int = 60,
        resolution: str = "1920x1080",
        warmup_frames: int = 15,
        anti_aliasing_samples: int = 8,
    ) -> RenderResult:
        """Render final cinematic video from Level Sequence using MRQ."""
        return render_sequence(
            scene_path=scene_path,
            output_path=output_path,
            fps=fps,
            resolution=resolution,
            warmup_frames=warmup_frames,
            anti_aliasing_samples=anti_aliasing_samples,
        )
