"""
Comprehensive Unit and Integration Test Suite for Unreal Engine 5 Bridge (Milestone 2).

Test Classes:
1. TestUE5ClientConnection: REST & WebSocket clients, serialization, headers, retry policy, offline fallback.
2. TestUE5MockServer: Lifecycle, dual-port binding (HTTP 30010 + WS 30020), thread safety, error resilience.
3. TestUE5AssetAndActors: Dynamic .glb/.fbx import, actor spawning, transforms, component hierarchy.
4. TestUE5PBRMaterials: PBR material instances, validation, clamping, texture set linking.
5. TestUE5LumenLighting: All 5 Lumen presets, intensity ranges, post-process volume GI settings.
6. TestUE5CineCameraChoreography: 5 camera presets, Look-At tracking math, beat sync, fallback timeline.
7. TestUE5MovieRenderQueue: MRQ configuration, warmup frames, telemetry bus progress, cancellation token.

100% Zero-Any compliant with Pydantic v2 strict models.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import threading
import time
from typing import Coroutine, Dict, Generator, List, Optional, Tuple, TypeVar, Union
import urllib.error
import urllib.request

import pytest
from pydantic import ValidationError

T = TypeVar("T")


def run_async(coro: Coroutine[object, object, T]) -> T:
    """Helper running an async coroutine synchronously using standard asyncio.run."""
    return asyncio.run(coro)

from backend.core.models import (
    CameraKeyframe,
    ColorRGB,
    MovieRenderQueueJobConfig,
    PBRTextureSet,
    ProgressEvent,
    RenderResult,
    Rotator3D,
    Vector3D,
)
from backend.core.telemetry import TelemetryBus
from backend.ue5.camera import CineCameraChoreographer, generate_camera_track
from backend.ue5.client import (
    AsyncUE5RemoteClient,
    AsyncUE5RestClient,
    AsyncUE5WebSocketClient,
    RetryConfig,
    UE5ParamDict,
    UE5RemoteClient,
    UE5RestClient,
    UE5WebSocketClient,
)
from backend.ue5.lighting import (
    LightActorConfig,
    LightingRig,
    LumenLightingSetup,
    setup_lumen_lighting,
)
from backend.ue5.materials import (
    MaterialManager,
    PBRMaterialInstance,
    create_pbr_material,
)
from backend.ue5.mock_server import UE5MockServer, UE5MockState, UE5RESTHandler
from backend.ue5.mrq import MRQManager, render_sequence
from tests.e2e.fixtures.synthetic_mesh import create_minimal_glb


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def ephemeral_mock_server() -> Generator[UE5MockServer, None, None]:
    """Provide an isolated UE5MockServer running on ephemeral test ports for the module."""
    server = UE5MockServer(host="127.0.0.1", port=30030, ws_port=30040)
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture(scope="module")
def ue5_test_client(ephemeral_mock_server: UE5MockServer) -> UE5RestClient:
    """Provide a UE5RestClient connected to the running ephemeral mock server."""
    return UE5RestClient(host=ephemeral_mock_server.host, port=ephemeral_mock_server.port)


@pytest.fixture
def mock_glb_file(tmp_path: Path) -> Path:
    """Create a temporary valid minimal binary GLB file fixture."""
    file_path = tmp_path / "test_model.glb"
    return create_minimal_glb(file_path, mesh_name="TestMesh")


# ---------------------------------------------------------------------------
# 1. Client Connection Handling & Serialization Tests
# ---------------------------------------------------------------------------

class TestUE5ClientConnection:
    """Validates REST and WebSocket client wire contracts, retries, and fallbacks."""

    def test_rest_call_serialization_nominal(self, ue5_test_client: UE5RestClient) -> None:
        res = ue5_test_client.call(
            object_path="/Script/UnrealEd.Default__EditorActorSubsystem",
            function_name="SpawnActor",
            parameters={"Class": "StaticMeshActor"},
            generate_transaction=True,
        )
        assert res.get("Success") is True
        assert "ActorId" in res
        actor_id = res.get("ActorId")
        assert isinstance(actor_id, str)
        assert "StaticMeshActor" in actor_id

    def test_rest_property_write_and_read(self, ue5_test_client: UE5RestClient) -> None:
        obj_path = "/Game/Stage_Main.PersistentLevel.Actor_1"
        prop_name = "CustomScalar"
        prop_val = 42.5

        set_res = ue5_test_client.set_property(obj_path, prop_name, prop_val)
        assert set_res.get("Success") is True

        read_val = ue5_test_client.get_property(obj_path, prop_name)
        assert read_val == prop_val

    def test_client_timeout_handling(self) -> None:
        # Client targeting a non-responsive address should terminate within timeout window
        client = UE5RestClient(host="10.255.255.1", port=30010, timeout=0.1, retry_config=RetryConfig(max_retries=0))
        start = time.time()
        res = client.call(
            object_path="/Script/Engine.Actor",
            function_name="TestTimeout",
        )
        elapsed = time.time() - start
        assert elapsed < 3.0
        # Should gracefully return simulated fallback response
        assert res.get("Success") is True

    def test_client_offline_graceful_fallback(self) -> None:
        offline_client = UE5RestClient(host="127.0.0.1", port=65530, retry_config=RetryConfig(max_retries=0))
        res = offline_client.call(
            object_path="/Script/Engine.Actor",
            function_name="CustomFunction",
            parameters={"Value": 10},
        )
        assert res.get("Success") is True
        assert res.get("Function") == "CustomFunction"

    def test_websocket_client_subscription_management(self) -> None:
        ws_client = UE5WebSocketClient(host="127.0.0.1", port=30040)
        events_received: List[str] = []

        def callback(event: UE5ParamDict) -> None:
            events_received.append("triggered")

        ws_client.subscribe("ActorSpawned", callback)
        assert callback in ws_client._subscriptions["ActorSpawned"]

        ws_client.trigger_event("ActorSpawned", {"ActorId": "TestActor_1"})
        assert len(events_received) == 1

        ws_client.unsubscribe("ActorSpawned", callback)
        assert callback not in ws_client._subscriptions["ActorSpawned"]

    def test_remote_client_facade(self, ephemeral_mock_server: UE5MockServer) -> None:
        remote = UE5RemoteClient(host=ephemeral_mock_server.host, http_port=ephemeral_mock_server.port)
        actor_id = remote.spawn_actor("CineCameraActor")
        assert "CineCameraActor" in actor_id

    def test_retry_policy_exponential_backoff(self) -> None:
        retry_cfg = RetryConfig(max_retries=3, base_delay_seconds=0.05, max_delay_seconds=0.5, jitter=False)
        d0 = retry_cfg.calculate_delay(0)
        d1 = retry_cfg.calculate_delay(1)
        d2 = retry_cfg.calculate_delay(2)
        assert round(d0, 3) == 0.05
        assert round(d1, 3) == 0.10
        assert round(d2, 3) == 0.20

    def test_async_rest_client_lifecycle(self, ephemeral_mock_server: UE5MockServer) -> None:
        async def _test() -> None:
            async with AsyncUE5RestClient(host=ephemeral_mock_server.host, port=ephemeral_mock_server.port) as client:
                res = await client.call(
                    object_path="/Script/UnrealEd.Default__EditorActorSubsystem",
                    function_name="SpawnActor",
                    parameters={"Class": "PointLight"},
                )
                assert res.get("Success") is True
                assert "PointLight" in str(res.get("ActorId"))

                set_res = await client.set_property("/Game/TestActor", "Intensity", 1000.0)
                assert set_res.get("Success") is True

                get_val = await client.get_property("/Game/TestActor", "Intensity")
                assert get_val == 1000.0

        run_async(_test())


# ---------------------------------------------------------------------------
# 2. Mock Server Lifecycle & Concurrency Tests
# ---------------------------------------------------------------------------

class TestUE5MockServer:
    """Validates mock server lifecycle, dual ports, concurrency, and route dispatch."""

    def test_mock_server_start_stop_lifecycle(self) -> None:
        server = UE5MockServer(host="127.0.0.1", port=30032, ws_port=30042)
        assert server.is_running is False
        server.start()
        assert server.is_running is True
        server.stop()
        assert server.is_running is False

    def test_mock_server_context_manager(self) -> None:
        with UE5MockServer(host="127.0.0.1", port=30033, ws_port=30043) as server:
            assert server.is_running is True
        assert server.is_running is False

    def test_mock_server_info_endpoint(self, ephemeral_mock_server: UE5MockServer) -> None:
        url = f"http://{ephemeral_mock_server.host}:{ephemeral_mock_server.port}/remote/info"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["Version"] == "5.4.0"
            assert data["Engine"] == "UnrealEngine"
            assert data["Mock"] is True

    def test_mock_server_root_endpoint(self, ephemeral_mock_server: UE5MockServer) -> None:
        url = f"http://{ephemeral_mock_server.host}:{ephemeral_mock_server.port}/"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["Status"] == "OK"
            assert data["ActiveLevel"] == "Stage_Main"

    def test_mock_server_reset_state(self, ue5_test_client: UE5RestClient, ephemeral_mock_server: UE5MockServer) -> None:
        ue5_test_client.spawn_actor("StaticMeshActor")
        assert len(ephemeral_mock_server.state.actors) > 4
        ephemeral_mock_server.reset_state()
        assert len(ephemeral_mock_server.state.actors) == 4

    def test_mock_server_thread_safety(self, ue5_test_client: UE5RestClient) -> None:
        def worker(idx: int) -> None:
            ue5_test_client.spawn_actor(f"WorkerActor_{idx}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_mock_server_malformed_json_resilience(self, ephemeral_mock_server: UE5MockServer) -> None:
        url = f"http://{ephemeral_mock_server.host}:{ephemeral_mock_server.port}/remote/object/call"
        req = urllib.request.Request(url, data=b"MALFORMED_BYTES{{{{", headers={"Content-Type": "application/json"}, method="PUT")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            assert resp.status == 200

    def test_mock_server_preset_endpoint(self, ephemeral_mock_server: UE5MockServer) -> None:
        url = f"http://{ephemeral_mock_server.host}:{ephemeral_mock_server.port}/remote/preset"
        req = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"}, method="PUT")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data.get("Success") is True

    def test_mock_server_dual_port_binding(self, ephemeral_mock_server: UE5MockServer) -> None:
        async def _test() -> None:
            # Port 30030 HTTP
            async with AsyncUE5RestClient(host=ephemeral_mock_server.host, port=ephemeral_mock_server.port) as rest:
                rest_res = await rest.call("/Script/Engine.Actor", "TestCall")
                assert rest_res.get("Success") is True

            # Port 30040 WebSocket
            async with AsyncUE5WebSocketClient(host=ephemeral_mock_server.host, port=ephemeral_mock_server.ws_port) as ws:
                ws_res = await ws.send_rpc(
                    verb="PUT",
                    url="/remote/object/call",
                    body={"objectPath": "/Script/Engine.Actor", "functionName": "TestWSCall"},
                )
                assert ws_res.get("ResponseCode") == 200

        run_async(_test())


# ---------------------------------------------------------------------------
# 3. Dynamic Asset Loading & Actor Transforms Tests
# ---------------------------------------------------------------------------

class TestUE5AssetAndActors:
    """Validates runtime mesh importing, spatial transform serialization, and component binding."""

    def test_dynamic_asset_import_valid_glb(self, ue5_test_client: UE5RestClient, mock_glb_file: Path) -> None:
        res = ue5_test_client.import_asset(str(mock_glb_file), "/Game/Imported/Meshes")
        assert res.get("Success") is True
        asset_path = str(res.get("AssetPath", ""))
        assert "/Game/Imported/Meshes/test_model" in asset_path

    def test_dynamic_asset_import_missing_file(self, ue5_test_client: UE5RestClient) -> None:
        res = ue5_test_client.import_asset("/non/existent/path/mesh.glb")
        assert res.get("Success") is False
        assert "does not exist" in str(res.get("Error", ""))

    def test_spawn_actor_with_models(self, ue5_test_client: UE5RestClient) -> None:
        loc = Vector3D(x=100.0, y=-250.0, z=120.0)
        rot = Rotator3D(pitch=15.0, yaw=90.0, roll=0.0)
        actor_id = ue5_test_client.spawn_actor("SkeletalMeshActor", location=loc, rotation=rot)
        assert "SkeletalMeshActor" in actor_id

    def test_spawn_actor_extreme_transforms(self, ue5_test_client: UE5RestClient) -> None:
        loc = Vector3D(x=-50000.0, y=-50000.0, z=-1000.0)
        rot = Rotator3D(pitch=-89.0, yaw=359.9, roll=0.0)
        actor_id = ue5_test_client.spawn_actor("StaticMeshActor", location=loc, rotation=rot)
        assert "StaticMeshActor" in actor_id

    def test_actor_material_assignment_function(self, ue5_test_client: UE5RestClient) -> None:
        actor_id = ue5_test_client.spawn_actor("StaticMeshActor")
        res = ue5_test_client.call(
            object_path="/Script/UnrealEd.Default__EditorActorSubsystem",
            function_name="SetMaterial",
            parameters={"ActorId": actor_id, "MaterialPath": "/Game/Materials/M_CharacterPBR"},
        )
        assert res.get("Success") is True
        assert res.get("Material") == "/Game/Materials/M_CharacterPBR"

    def test_actor_location_and_rotation_update(self, ue5_test_client: UE5RestClient, ephemeral_mock_server: UE5MockServer) -> None:
        actor_id = ue5_test_client.spawn_actor("CineCameraActor")
        res = ue5_test_client.call(
            object_path=actor_id,
            function_name="SetActorLocationAndRotation",
            parameters={
                "ActorId": actor_id,
                "Location": {"X": 200.0, "Y": -150.0, "Z": 80.0},
                "Rotation": {"Pitch": -10.0, "Yaw": 45.0, "Roll": 0.0},
            },
        )
        assert res.get("Success") is True
        actor_state = ephemeral_mock_server.state.actors.get(actor_id)
        assert actor_state is not None
        assert actor_state.get("location") == {"X": 200.0, "Y": -150.0, "Z": 80.0}


# ---------------------------------------------------------------------------
# 4. PBR Materials Tests
# ---------------------------------------------------------------------------

class TestUE5PBRMaterials:
    """Validates PBR material parameter clamping, strict validation, and texture linking."""

    def test_pbr_material_bounds_validation(self) -> None:
        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="InvalidMat", roughness=1.5)

        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="InvalidMat", metallic=-0.2)

        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="InvalidMat", specular=2.0)

    def test_material_manager_create_and_get(self) -> None:
        manager = MaterialManager()
        mat = manager.create_material(
            "M_Gold",
            base_color=ColorRGB(r=1.0, g=0.8, b=0.2),
            roughness=0.3,
            metallic=1.0,
            specular=0.5,
        )
        assert mat.material_name == "M_Gold"
        assert manager.get_material("M_Gold") == mat
        assert manager.get_material("M_NonExistent") is None
        assert "M_Gold" in manager.list_materials()

    def test_material_manager_clamping_logic(self) -> None:
        manager = MaterialManager()
        mat = manager.create_material("M_Clamped", roughness=2.5, metallic=-1.0, specular=5.0)
        assert mat.roughness == 1.0
        assert mat.metallic == 0.0
        assert mat.specular == 1.0

    def test_create_pbr_material_facade(self) -> None:
        mat = create_pbr_material(
            name="M_TestFacade",
            base_color={"r": 0.2, "g": 0.4, "b": 0.8},
            roughness=0.6,
            metallic=0.1,
            textures={"albedo_path": "/tmp/albedo.png", "normal_path": "/tmp/normal.png"},
        )
        assert mat.base_color.b == 0.8
        assert mat.roughness == 0.6
        assert mat.textures is not None
        assert mat.textures.albedo_path == "/tmp/albedo.png"

    def test_pbr_material_to_ue5_parameters(self) -> None:
        mat = create_pbr_material(
            name="M_Export",
            base_color={"r": 1.0, "g": 1.0, "b": 1.0},
            roughness=0.4,
            metallic=0.8,
            textures={"albedo_path": "/Game/Textures/T_Albedo.png"},
        )
        params = mat.to_ue5_parameters()
        assert params["Roughness"] == 0.4
        assert params["Metallic"] == 0.8
        assert params["AlbedoMap"] == "/Game/Textures/T_Albedo.png"
        assert isinstance(params["BaseColor"], dict)


# ---------------------------------------------------------------------------
# 5. Lumen Lighting Tests
# ---------------------------------------------------------------------------

class TestUE5LumenLighting:
    """Validates 5 Lumen lighting presets, intensity calibrations, and post-process settings."""

    def test_lighting_presets_all_5(self) -> None:
        presets = [
            "studio_3point",
            "cyberpunk_neon",
            "dramatic",
            "outdoor_sunlight",
            "night_moonlight",
        ]
        for p in presets:
            setup = setup_lumen_lighting(p)
            assert isinstance(setup, LumenLightingSetup)
            assert len(setup.lights) >= 2
            assert setup.lumen_global_illumination is True
            assert setup.lumen_reflections is True

    def test_unknown_preset_fallback(self) -> None:
        setup = setup_lumen_lighting("non_existent_preset_xyz")
        assert setup.preset_name == "studio_3point"
        assert len(setup.lights) == 4

    def test_light_actor_config_model_validation(self) -> None:
        light = LightActorConfig(
            name="Key_Special",
            light_type="Spot",
            intensity=25000.0,
            color=ColorRGB(r=1.0, g=0.9, b=0.8),
            position=Vector3D(x=100.0, y=-200.0, z=300.0),
            rotation=Rotator3D(pitch=-30.0, yaw=45.0, roll=0.0),
            cast_shadows=True,
            temperature_kelvin=5500.0,
        )
        assert light.name == "Key_Special"
        assert light.intensity == 25000.0
        assert light.temperature_kelvin == 5500.0

    def test_lumen_postprocess_volume_flags(self) -> None:
        setup = setup_lumen_lighting("studio_3point")
        assert setup.lumen_global_illumination is True
        assert setup.lumen_reflections is True
        assert setup.indirect_lighting_intensity >= 1.0


# ---------------------------------------------------------------------------
# 6. CineCamera Choreography Tests
# ---------------------------------------------------------------------------

class TestUE5CineCameraChoreography:
    """Validates CineCamera presets, Look-At tracking math, FOV clamping, and fallback timeline."""

    def test_camera_choreographer_initialization_bounds(self) -> None:
        choreographer = CineCameraChoreographer(default_fov=5.0, distance=20.0)
        assert choreographer.default_fov == 10.0  # Clamped to min 10
        assert choreographer.distance == 50.0      # Clamped to min 50

        choreographer2 = CineCameraChoreographer(default_fov=150.0, distance=500.0)
        assert choreographer2.default_fov == 120.0 # Clamped to max 120

    def test_empty_beats_fallback(self) -> None:
        choreographer = CineCameraChoreographer()
        track = choreographer.generate_track(beat_timestamps=[], total_duration=6.0)
        assert len(track) == 2
        assert track[0].time == 0.0
        assert track[1].time == 6.0
        assert track[0].fov == 45.0
        assert track[1].fov == 45.0

    def test_camera_presets_generation_all_5(self) -> None:
        beats = [1.0, 2.0, 3.0, 4.0]
        duration = 5.0
        presets = ["smooth_orbit", "dramatic_orbit", "aerial_pan", "front_close", "spiral_ascent"]

        for preset in presets:
            track = generate_camera_track(beats, duration, preset=preset)
            assert len(track) >= len(beats)
            assert all(isinstance(kf, CameraKeyframe) for kf in track)
            payload = track[0].to_ue5_payload()
            assert "Location" in payload
            assert "Rotation" in payload
            assert "FieldOfView" in payload

    def test_look_at_math_calculation(self) -> None:
        # Camera at (0, -400, 120) looking towards origin (0, 0, 120)
        cam = Vector3D(x=0.0, y=-400.0, z=120.0)
        target = Vector3D(x=0.0, y=0.0, z=120.0)
        pitch, yaw = CineCameraChoreographer.calculate_look_at(cam, target)
        assert pitch == 0.0
        assert yaw == 90.0

        # Looking up towards elevated target
        elevated_target = Vector3D(x=0.0, y=0.0, z=520.0)
        pitch_up, yaw_up = CineCameraChoreographer.calculate_look_at(cam, elevated_target)
        assert pitch_up == 45.0
        assert yaw_up == 90.0

    def test_camera_keyframe_ue5_payload_formatting(self) -> None:
        kf = CameraKeyframe(
            time=1.5,
            x=100.0,
            y=-350.0,
            z=130.0,
            pitch=-5.0,
            yaw=45.0,
            roll=0.0,
            fov=50.0,
            focal_length=35.0,
            aperture=2.8,
            focus_distance=350.0,
        )
        payload = kf.to_ue5_payload()
        assert payload["Location"]["X"] == 100.0
        assert payload["Rotation"]["Yaw"] == 45.0
        assert payload["FieldOfView"] == 50.0


# ---------------------------------------------------------------------------
# 7. Movie Render Queue Tests
# ---------------------------------------------------------------------------

class TestUE5MovieRenderQueue:
    """Validates MRQ scheduling, warmup simulation, non-blocking telemetry, and video output."""

    def test_mrq_job_config_model_validation(self) -> None:
        config = MovieRenderQueueJobConfig(
            scene_path="/Game/Sequences/LS_Test",
            output_path="/renders/out.mp4",
            resolution="1920x1080",
            fps=60,
            warmup_frames=30,
        )
        assert config.get_resolution_dimensions() == (1920, 1080)
        assert config.fps == 60

    def test_mrq_job_config_invalid_resolution_regex(self) -> None:
        with pytest.raises(ValidationError):
            MovieRenderQueueJobConfig(
                scene_path="LS",
                output_path="out.mp4",
                resolution="invalid_resolution",
            )

    def test_mrq_manager_render_execution(self, tmp_path: Path) -> None:
        out_video = tmp_path / "cinematic_output.mp4"
        manager = MRQManager(output_dir=tmp_path)
        res = manager.render(
            scene_path="/Game/Sequences/LS_Stage",
            output_path=str(out_video),
            fps=30,
            resolution="1280x720",
        )
        assert isinstance(res, RenderResult)
        assert res.success is True
        assert res.frame_count == 90  # 3s * 30fps
        assert res.file_size_bytes > 0
        assert out_video.exists()

    def test_render_sequence_functional_facade(self, tmp_path: Path) -> None:
        out_video = tmp_path / "facade_render.mp4"
        res = render_sequence(
            scene_path="/Game/Sequences/LS_Stage",
            output_path=str(out_video),
            fps=24,
            resolution="1920x1080",
        )
        assert res.success is True
        assert res.frame_count == 72  # 3s * 24fps
        assert out_video.exists()

    def test_mrq_async_progress_telemetry(self, tmp_path: Path) -> None:
        async def _test() -> None:
            out_video = tmp_path / "async_telemetry_test.mp4"
            bus = TelemetryBus()
            events_captured: List[ProgressEvent] = []

            def on_event(ev: object) -> None:
                if isinstance(ev, ProgressEvent) and ev.stage == "mrq_render":
                    events_captured.append(ev)

            bus.subscribe(on_event)
            manager = MRQManager(output_dir=tmp_path, telemetry_bus=bus)

            job_config = MovieRenderQueueJobConfig(
                scene_path="/Game/Sequences/LS_Stage",
                output_path=str(out_video),
                fps=30,
                resolution="1280x720",
                warmup_frames=5,
            )
            res = await manager.render_async(job_config, duration_seconds=1.0)
            assert res.success is True
            assert len(events_captured) > 0
            # Verify progression from warmup to 100%
            percentages = [ev.percentage for ev in events_captured]
            assert percentages[-1] == 100.0

        run_async(_test())

    def test_mrq_cancellation_token(self, tmp_path: Path) -> None:
        async def _test() -> None:
            out_video = tmp_path / "cancelled_render.mp4"
            cancel_token = asyncio.Event()
            cancel_token.set()  # Cancel immediately

            manager = MRQManager(output_dir=tmp_path)
            job_config = MovieRenderQueueJobConfig(
                scene_path="/Game/Sequences/LS_Stage",
                output_path=str(out_video),
                fps=30,
                resolution="1280x720",
            )

            with pytest.raises(asyncio.CancelledError):
                await manager.render_async(job_config, cancellation_token=cancel_token)

        run_async(_test())
