"""
Adversarial Stress Test Suite for Milestone 2: UE5 Bridge & Mock Server.

Empirical Challenger tests focusing on:
1. High-concurrency RPC calls to UE5MockServer across multiple threads.
2. Rapid server start/stop cycles and socket reuse on ports 30010 and 30020.
3. CineCamera Look-At trajectory math with boundary coordinates (collinear, vertical pitch +-90 deg, zero distance).
4. Cooperative cancellation of MRQ render jobs via asyncio.Event.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import math
from pathlib import Path
import threading
import time
from typing import Dict, List, Optional, Tuple, Union
import urllib.request
import urllib.error

import pytest
import websockets

from backend.core.models import (
    CameraKeyframe,
    MovieRenderQueueJobConfig,
    ProgressEvent,
    RenderResult,
    Rotator3D,
    Vector3D,
)
from backend.core.telemetry import TelemetryBus
from backend.ue5.camera import CineCameraChoreographer, generate_camera_track
from backend.ue5.client import (
    AsyncUE5RestClient,
    AsyncUE5WebSocketClient,
    RetryConfig,
    UE5ParamDict,
    UE5RestClient,
    UE5WebSocketClient,
)
from backend.ue5.mock_server import UE5MockServer, UE5MockState
from backend.ue5.mrq import MRQManager


def run_async(coro):
    return asyncio.run(coro)


# ===========================================================================
# 1. High-Concurrency Stress Tests
# ===========================================================================

@pytest.fixture(scope="module")
def concurrent_server():
    server = UE5MockServer(host="127.0.0.1", port=30070, ws_port=30080)
    server.start()
    time.sleep(0.1)
    yield server
    server.stop()


class TestHighConcurrencyRPC:
    """Stress tests for UE5MockServer under heavy concurrent multi-threaded load."""


    def test_high_concurrency_threaded_rest_calls(self, concurrent_server: UE5MockServer) -> None:
        """
        Execute 100 concurrent REST RPC requests from 20 worker threads.
        Verifies:
        - No connection drops or socket starvation.
        - State consistency in UE5MockState (actors spawned, materials updated).
        - Correct actor count and ID incrementing.
        """
        num_workers = 20
        requests_per_worker = 5
        total_requests = num_workers * requests_per_worker

        def worker_task(worker_id: int) -> List[Dict[str, Union[str, bool, int]]]:
            client = UE5RestClient(
                host=concurrent_server.host,
                port=concurrent_server.port,
                timeout=5.0,
                retry_config=RetryConfig(max_retries=2, base_delay_seconds=0.05),
            )
            results: List[Dict[str, Union[str, bool, int]]] = []
            for i in range(requests_per_worker):
                # 1. Spawn actor
                spawn_res = client.call(
                    object_path="/Script/UnrealEd.Default__EditorActorSubsystem",
                    function_name="SpawnActor",
                    parameters={
                        "Class": f"WorkerActor_{worker_id}",
                        "Location": {"X": float(worker_id * 100 + i), "Y": 0.0, "Z": 50.0},
                    },
                )
                actor_id = spawn_res.get("ActorId")
                results.append({"type": "spawn", "success": bool(spawn_res.get("Success")), "actor_id": str(actor_id)})

                # 2. Set property
                if actor_id:
                    prop_res = client.set_property(
                        object_path=str(actor_id),
                        property_name="worker_tag",
                        value=f"w{worker_id}_req{i}",
                    )
                    results.append({"type": "set_prop", "success": bool(prop_res.get("Success"))})

            return results

        all_results: List[Dict[str, Union[str, bool, int]]] = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, w) for w in range(num_workers)]
            for fut in as_completed(futures):
                all_results.extend(fut.result())

        # Assertions
        assert len(all_results) == total_requests * 2
        failures = [r for r in all_results if not r["success"]]
        assert len(failures) == 0, f"Encountered {len(failures)} failed requests under concurrency"

        # State check: verify actors in server state
        spawn_results = [r for r in all_results if r["type"] == "spawn"]
        actor_ids = {r["actor_id"] for r in spawn_results}
        assert len(actor_ids) == total_requests, f"Expected {total_requests} unique actor IDs, got {len(actor_ids)}"

    def test_concurrent_websocket_rpc_and_subscriptions(self, concurrent_server: UE5MockServer) -> None:
        """
        Execute concurrent WebSocket RPC calls and broadcast property events.
        Verifies:
        - Multiple simultaneous async coroutines sending RPC messages over WebSocket.
        - Event notifications dispatched cleanly without coroutine exceptions.
        """
        async def run_ws_stress() -> None:
            received_events: List[UE5ParamDict] = []
            event_received = asyncio.Event()

            def on_property_changed(event: UE5ParamDict) -> None:
                received_events.append(event)
                if len(received_events) >= 5:
                    event_received.set()

            client = AsyncUE5WebSocketClient(
                host=concurrent_server.host,
                port=concurrent_server.ws_port,
                timeout=5.0,
            )
            await client.connect()

            # Subscribe to PropertyChanged
            client.subscribe("PropertyChanged", on_property_changed)

            # Concurrent RPC invocations
            async def send_single_rpc(idx: int) -> UE5ParamDict:
                return await client.send_rpc(
                    verb="PUT",
                    url="/remote/object/call",
                    body={
                        "objectPath": f"/Game/TestActor_{idx}",
                        "functionName": "SetActorLocationAndRotation",
                        "parameters": {"Location": {"X": float(idx), "Y": 0.0, "Z": 0.0}},
                    },
                )

            tasks = [asyncio.create_task(send_single_rpc(i)) for i in range(20)]
            responses = await asyncio.gather(*tasks)

            assert len(responses) == 20
            for resp in responses:
                assert resp.get("ResponseCode") == 200

            # Trigger property changes to test event broadcast
            for i in range(5):
                concurrent_server.state.set_property(
                    object_path=f"/Game/TestActor_{i}",
                    property_name="test_prop",
                    value=f"val_{i}",
                )

            try:
                await asyncio.wait_for(event_received.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass

            assert len(received_events) >= 5
            await client.disconnect()

        asyncio.run(run_ws_stress())

    def test_websocket_pipelined_multi_client_concurrency(self, concurrent_server: UE5MockServer) -> None:
        """
        Stress test 5 concurrent WebSocket clients, each dispatching 10 pipelined RPCs simultaneously.
        Verifies:
        - Total 50 in-flight requests correctly matched by RequestId across separate client sessions.
        - Zero dropped futures or asyncio timeouts.
        """
        async def run_multi_client() -> None:
            num_clients = 5
            rpcs_per_client = 10

            async def client_worker(client_id: int) -> List[UE5ParamDict]:
                c = AsyncUE5WebSocketClient(
                    host=concurrent_server.host,
                    port=concurrent_server.ws_port,
                    timeout=5.0,
                )
                await c.connect()
                try:
                    tasks = []
                    for r in range(rpcs_per_client):
                        coro = c.send_rpc(
                            verb="PUT",
                            url="/remote/object/call",
                            body={
                                "objectPath": f"/Game/MultiClientActor_{client_id}_{r}",
                                "functionName": "SpawnActor",
                                "parameters": {"Class": "StaticMeshActor"},
                            },
                        )
                        tasks.append(asyncio.create_task(coro))
                    return await asyncio.gather(*tasks)
                finally:
                    await c.disconnect()

            client_tasks = [asyncio.create_task(client_worker(c)) for c in range(num_clients)]
            grouped_responses = await asyncio.gather(*client_tasks)

            total_resps = sum(len(g) for g in grouped_responses)
            assert total_resps == num_clients * rpcs_per_client
            for group in grouped_responses:
                for resp in group:
                    assert resp.get("ResponseCode") == 200
                    body = resp.get("ResponseBody")
                    assert isinstance(body, dict) and body.get("Success") is True

        asyncio.run(run_multi_client())

    def test_mock_server_concurrent_mixed_read_write_heavy(self, concurrent_server: UE5MockServer) -> None:
        """
        Multi-threaded stress test hammering set_property and get_property across 10 threads.
        Verifies:
        - Thread safety under simultaneous read/write collisions on identical properties.
        - No deadlocks on UE5MockState._lock.
        """
        num_threads = 10
        ops_per_thread = 20
        errors: List[str] = []

        def worker(tid: int) -> None:
            client = UE5RestClient(host=concurrent_server.host, port=concurrent_server.port, timeout=5.0)
            target_obj = f"/Game/SharedActor_{tid % 3}"  # 3 shared objects to force contention
            for op in range(ops_per_thread):
                val = f"thread_{tid}_val_{op}"
                # Write
                res_w = client.set_property(target_obj, "SharedProp", val)
                if not res_w.get("Success"):
                    errors.append(f"Write failed at tid={tid}, op={op}")
                # Read back
                res_r = client.get_property(target_obj, "SharedProp")
                if res_r is None:
                    errors.append(f"Read returned None at tid={tid}, op={op}")

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
        for th in threads:
            th.start()
        for th in threads:
            th.join(timeout=10.0)

        assert len(errors) == 0, f"Errors during heavy read/write contention: {errors[:5]}"

    def test_malformed_and_extreme_rest_payloads(self, concurrent_server: UE5MockServer) -> None:
        """
        Test server resilience against malformed, deeply nested, or oversized JSON payloads.
        """
        base_url = f"http://{concurrent_server.host}:{concurrent_server.port}"

        # 1. Non-JSON raw bytes
        req = urllib.request.Request(
            f"{base_url}/remote/object/call",
            data=b"THIS_IS_NOT_JSON!@#$%",
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert resp.status == 200
            assert data.get("Success") is True  # Gracefully handles malformed payload

        # 2. Large 64KB payload
        large_dict = {f"k_{i}": "x" * 256 for i in range(256)}
        large_json = json.dumps({"objectPath": "/Game/Test", "parameters": large_dict}).encode("utf-8")
        req_large = urllib.request.Request(
            f"{base_url}/remote/object/call",
            data=large_json,
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with urllib.request.urlopen(req_large, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert resp.status == 200
            assert data.get("Success") is True



# ===========================================================================
# 2. Server Lifecycle & Rapid Start/Stop Socket Reuse Stress Tests
# ===========================================================================

class TestServerLifecycleAndSocketReuse:
    """Stress tests rapid start/stop cycles and socket address reuse on ports 30010 & 30020."""

    def test_rapid_start_stop_cycles_default_ports(self) -> None:
        """
        Perform 5 rapid start/stop cycles on ports 30010 (HTTP) and 30020 (WS).
        Verifies:
        - SO_REUSEADDR prevents WinError 10048 (address in use).
        - HTTP and WS endpoints respond successfully after each restart.
        - Sockets are cleanly torn down upon server.stop().
        """
        test_port = 30010
        test_ws_port = 30020

        for cycle in range(5):
            server = UE5MockServer(host="127.0.0.1", port=test_port, ws_port=test_ws_port)
            server.start()
            assert server.is_running, f"Server failed to start on cycle {cycle}"

            # Verify HTTP port is responsive
            url = f"http://127.0.0.1:{test_port}/remote/info"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                assert body.get("Mock") is True, f"HTTP info endpoint returned invalid data on cycle {cycle}"

            # Verify WebSocket port is responsive
            async def check_ws() -> None:
                uri = f"ws://127.0.0.1:{test_ws_port}/remote/protocol"
                async with websockets.connect(uri, close_timeout=2.0) as ws:
                    assert ws.state is websockets.State.OPEN

            asyncio.run(check_ws())

            # Stop server cleanly
            server.stop()
            assert not server.is_running

            # Brief pause to verify socket release
            time.sleep(0.05)

    def test_server_idempotent_double_start_stop(self) -> None:
        """Calling start() twice or stop() twice must not crash or leak resources."""
        server = UE5MockServer(host="127.0.0.1", port=30090, ws_port=30095)
        try:
            server.start()
            assert server.is_running
            # Second start should be a harmless no-op
            server.start()
            assert server.is_running
        finally:
            server.stop()
            assert not server.is_running
            # Second stop should be a harmless no-op
            server.stop()
            assert not server.is_running


# ===========================================================================
# 3. CineCamera Boundary & Trajectory Math Stress Tests
# ===========================================================================

class TestCineCameraBoundaryMath:
    """Mathematical stress tests for Look-At tracking and trajectory keyframe generation."""

    def test_look_at_zero_distance_singularity(self) -> None:
        """
        Camera position exactly coincides with target position.
        Must not divide by zero or yield NaN.
        """
        pos = Vector3D(x=100.0, y=200.0, z=300.0)
        pitch, yaw = CineCameraChoreographer.calculate_look_at(cam_pos=pos, target_pos=pos)
        assert not math.isnan(pitch) and not math.isnan(yaw)
        assert not math.isinf(pitch) and not math.isinf(yaw)
        assert pitch == 0.0
        assert yaw == 0.0

    def test_look_at_vertical_pitch_boundaries(self) -> None:
        """
        Camera directly below (+90 deg pitch) and directly above (-90 deg pitch).
        """
        target = Vector3D(x=0.0, y=0.0, z=500.0)

        # Directly below: looking straight up
        cam_below = Vector3D(x=0.0, y=0.0, z=0.0)
        pitch_up, yaw_up = CineCameraChoreographer.calculate_look_at(cam_below, target)
        assert abs(pitch_up - 90.0) < 0.1, f"Expected +90 pitch, got {pitch_up}"
        assert not math.isnan(yaw_up)

        # Directly above: looking straight down
        cam_above = Vector3D(x=0.0, y=0.0, z=1000.0)
        pitch_down, yaw_down = CineCameraChoreographer.calculate_look_at(cam_above, target)
        assert abs(pitch_down - (-90.0)) < 0.1, f"Expected -90 pitch, got {pitch_down}"
        assert not math.isnan(yaw_down)

    def test_look_at_collinear_axis_orientations(self) -> None:
        """
        Camera and target strictly aligned along canonical axes.
        Unreal convention: X forward (0 deg), Y right (+90 deg), -Y left (-90 deg), -X backward (180 deg).
        """
        center = Vector3D(x=0.0, y=0.0, z=0.0)

        # Facing along +X
        p_x, y_x = CineCameraChoreographer.calculate_look_at(cam_pos=Vector3D(x=-100.0, y=0.0, z=0.0), target_pos=center)
        assert p_x == 0.0
        assert y_x == 0.0

        # Facing along -X (target at negative X)
        p_neg_x, y_neg_x = CineCameraChoreographer.calculate_look_at(cam_pos=Vector3D(x=100.0, y=0.0, z=0.0), target_pos=center)
        assert p_neg_x == 0.0
        assert abs(y_neg_x - 180.0) < 0.1 or abs(y_neg_x - (-180.0)) < 0.1

        # Facing along +Y
        p_y, y_y = CineCameraChoreographer.calculate_look_at(cam_pos=Vector3D(x=0.0, y=-100.0, z=0.0), target_pos=center)
        assert p_y == 0.0
        assert abs(y_y - 90.0) < 0.1

        # Facing along -Y
        p_neg_y, y_neg_y = CineCameraChoreographer.calculate_look_at(cam_pos=Vector3D(x=0.0, y=100.0, z=0.0), target_pos=center)
        assert p_neg_y == 0.0
        assert abs(y_neg_y - (-90.0)) < 0.1

    def test_generate_track_boundary_inputs(self) -> None:
        """
        Stress test generate_track with boundary conditions:
        - Empty beat list
        - Negative beat timestamps
        - Duplicate beat timestamps
        - Beats strictly beyond duration
        - Zero / near-zero duration
        - Negative or extreme FOV / distance parameters
        """
        choreographer = CineCameraChoreographer(default_fov=-10.0, distance=-50.0)
        # Clamped properties
        assert choreographer.default_fov == 10.0  # Clamped to min 10
        assert choreographer.distance == 50.0    # Clamped to min 50

        # Boundary 1: Negative / out-of-bounds beats with zero duration
        kfs = choreographer.generate_track(
            beat_timestamps=[-5.0, -1.0, 100.0],
            total_duration=0.0,
            preset="smooth_orbit",
        )
        assert len(kfs) >= 2
        for kf in kfs:
            assert isinstance(kf, CameraKeyframe)
            assert not math.isnan(kf.x) and not math.isnan(kf.y) and not math.isnan(kf.z)
            assert 10.0 <= kf.fov <= 120.0
            assert kf.focal_length >= 1.0

        # Boundary 2: Duplicate beat timestamps
        kfs_dups = choreographer.generate_track(
            beat_timestamps=[1.0, 1.0, 1.0, 2.5, 2.5],
            total_duration=5.0,
            preset="spiral_ascent",
        )
        assert len(kfs_dups) >= 2
        for kf in kfs_dups:
            assert 0.0 <= kf.time <= 5.0
            assert kf.focus_distance >= 50.0

        # Boundary 3: All 5 presets survive extreme center_z
        presets = ["smooth_orbit", "dramatic_orbit", "aerial_pan", "front_close", "spiral_ascent"]
        for p in presets:
            res = choreographer.generate_track(
                beat_timestamps=[0.5, 1.0, 1.5],
                total_duration=2.0,
                preset=p,
                center_z=10000.0,
            )
            assert len(res) >= 2
            for kf in res:
                assert not math.isnan(kf.pitch)
                assert not math.isnan(kf.yaw)

    def test_look_at_extreme_floats(self) -> None:
        """
        Verify Look-At computation withstands extreme floating-point coordinates without overflow.
        """
        # Huge coordinates (1e12 cm = 10,000,000 km)
        cam_huge = Vector3D(x=1e12, y=1e12, z=1e12)
        target_huge = Vector3D(x=-1e12, y=-1e12, z=-1e12)
        p, y = CineCameraChoreographer.calculate_look_at(cam_huge, target_huge)
        assert not math.isnan(p) and not math.isnan(y)
        assert -90.0 <= p <= 90.0
        assert -180.0 <= y <= 180.0

        # Microscopic coordinates (1e-9)
        cam_tiny = Vector3D(x=1e-9, y=0.0, z=0.0)
        target_tiny = Vector3D(x=0.0, y=0.0, z=0.0)
        p_tiny, y_tiny = CineCameraChoreographer.calculate_look_at(cam_tiny, target_tiny)
        assert not math.isnan(p_tiny) and not math.isnan(y_tiny)
        assert abs(y_tiny - 180.0) < 0.1 or abs(y_tiny - (-180.0)) < 0.1


# ===========================================================================
# 4. MRQ Cooperative Cancellation Stress Tests

# ===========================================================================

class TestMRQCooperativeCancellation:
    """Stress tests cooperative cancellation of MRQ render jobs via asyncio.Event."""

    def test_cancellation_pre_set_token(self, tmp_path: Path) -> None:
        """Token cancelled before render_async is even called."""
        async def _test() -> None:
            out_file = tmp_path / "cancelled_pre.mp4"
            bus = TelemetryBus()
            manager = MRQManager(output_dir=tmp_path, telemetry_bus=bus)

            config = MovieRenderQueueJobConfig(
                scene_path="/Game/Stage_Main",
                output_path=str(out_file),
                fps=30,
                warmup_frames=20,
            )

            cancel_event = asyncio.Event()
            cancel_event.set()  # Cancelled immediately

            with pytest.raises(asyncio.CancelledError) as exc_info:
                await manager.render_async(
                    job_config=config,
                    cancellation_token=cancel_event,
                    duration_seconds=2.0,
                )

            assert "warmup" in str(exc_info.value).lower()
            # Verify file was never finalized
            assert not out_file.exists()

        run_async(_test())

    def test_cancellation_during_warmup(self, tmp_path: Path) -> None:
        """Token cancelled during warmup frame simulation."""
        async def _test() -> None:
            out_file = tmp_path / "cancelled_warmup.mp4"
            bus = TelemetryBus()
            manager = MRQManager(output_dir=tmp_path, telemetry_bus=bus)

            config = MovieRenderQueueJobConfig(
                scene_path="/Game/Stage_Main",
                output_path=str(out_file),
                fps=30,
                warmup_frames=50,
            )

            cancel_event = asyncio.Event()

            async def cancel_delayed() -> None:
                await asyncio.sleep(0.03)
                cancel_event.set()

            asyncio.create_task(cancel_delayed())

            with pytest.raises(asyncio.CancelledError) as exc_info:
                await manager.render_async(
                    job_config=config,
                    cancellation_token=cancel_event,
                    duration_seconds=3.0,
                )

            assert "warmup" in str(exc_info.value).lower()
            assert not out_file.exists()

        run_async(_test())

    def test_cancellation_during_main_render_frames(self, tmp_path: Path) -> None:
        """Token cancelled during main frame rendering loop."""
        async def _test() -> None:
            out_file = tmp_path / "cancelled_frames.mp4"
            bus = TelemetryBus()
            manager = MRQManager(output_dir=tmp_path, telemetry_bus=bus)

            config = MovieRenderQueueJobConfig(
                scene_path="/Game/Stage_Main",
                output_path=str(out_file),
                fps=60,
                warmup_frames=2,  # Very short warmup so it enters main loop quickly
            )

            cancel_event = asyncio.Event()

            async def cancel_delayed() -> None:
                await asyncio.sleep(0.02)
                cancel_event.set()

            asyncio.create_task(cancel_delayed())

            with pytest.raises(asyncio.CancelledError) as exc_info:
                await manager.render_async(
                    job_config=config,
                    cancellation_token=cancel_event,
                    duration_seconds=5.0,  # 300 frames total
                )

            assert "frame" in str(exc_info.value).lower()
            assert not out_file.exists()

        run_async(_test())

    def test_concurrent_mixed_cancellation_and_completion(self, tmp_path: Path) -> None:
        """
        Run 4 concurrent MRQ jobs: cancel 2 and allow 2 to complete to 100%.
        Verifies:
        - Cancellation tokens do not interfere with concurrently running uncancelled jobs.
        - Uncancelled jobs produce valid MP4 video containers and return success.
        - Cancelled jobs abort cleanly.
        """
        async def _test() -> None:
            bus = TelemetryBus()
            manager = MRQManager(output_dir=tmp_path, telemetry_bus=bus)

            out_c1 = tmp_path / "job_cancel_1.mp4"
            out_c2 = tmp_path / "job_cancel_2.mp4"
            out_ok1 = tmp_path / "job_ok_1.mp4"
            out_ok2 = tmp_path / "job_ok_2.mp4"

            token_c1 = asyncio.Event()
            token_c2 = asyncio.Event()
            token_ok1: Optional[asyncio.Event] = None
            token_ok2: Optional[asyncio.Event] = None

            token_c1.set()  # Cancelled before start

            async def cancel_c2_delayed() -> None:
                await asyncio.sleep(0.02)
                token_c2.set()

            asyncio.create_task(cancel_c2_delayed())

            cfg_c1 = MovieRenderQueueJobConfig(scene_path="/Game/S1", output_path=str(out_c1), fps=30, warmup_frames=10)
            cfg_c2 = MovieRenderQueueJobConfig(scene_path="/Game/S2", output_path=str(out_c2), fps=30, warmup_frames=20)
            cfg_ok1 = MovieRenderQueueJobConfig(scene_path="/Game/S3", output_path=str(out_ok1), fps=30, warmup_frames=2)
            cfg_ok2 = MovieRenderQueueJobConfig(scene_path="/Game/S4", output_path=str(out_ok2), fps=30, warmup_frames=2)

            results: Dict[str, Union[RenderResult, str]] = {}

            async def run_job(name: str, cfg: MovieRenderQueueJobConfig, tok: Optional[asyncio.Event]) -> None:
                try:
                    res = await manager.render_async(cfg, cancellation_token=tok, duration_seconds=0.5)
                    results[name] = res
                except asyncio.CancelledError:
                    results[name] = "CANCELLED"

            await asyncio.gather(
                run_job("c1", cfg_c1, token_c1),
                run_job("c2", cfg_c2, token_c2),
                run_job("ok1", cfg_ok1, token_ok1),
                run_job("ok2", cfg_ok2, token_ok2),
            )

            assert results["c1"] == "CANCELLED"
            assert results["c2"] == "CANCELLED"
            assert isinstance(results["ok1"], RenderResult)
            assert isinstance(results["ok2"], RenderResult)
            assert results["ok1"].success is True
            assert results["ok2"].success is True
            assert out_ok1.exists() and out_ok1.stat().st_size > 0
            assert out_ok2.exists() and out_ok2.stat().st_size > 0
            assert not out_c1.exists()

        run_async(_test())

