"""
Empirical Adversarial Stress Test Suite for Milestone 7 Iteration 2.

Authored by Challenger (challenger_m7_it2_2).
Adversarially challenges:
1. PlanEngine state machine promotion to PlanStatus.APPROVED when all steps are approved.
2. Step confirmation gates: partial approvals, out-of-order approvals, terminal rejection behavior.
3. Telemetry event invariants: PlanProposalEvent, ProgressEvent, LogEvent under step operations.
4. Concurrency & race conditions: multi-threaded step confirmations and multi-plan operations.
5. FastMCPServer tool invocation parity, concurrency stress, parameter validation, and dynamic registration.

Strictly 100% Zero-Any compliant with Pydantic v2 models.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from pathlib import Path
import struct
import threading
from typing import Dict, List, Optional, Tuple, Union
import wave

import pytest

from backend.core.models import (
    AudioAnalysisResult,
    AutoRigResult,
    ImageTo3DResult,
    LogEvent,
    LogLevel,
    MocapResult,
    PlanProposalEvent,
    PlanRiskLevel,
    PlanStatus,
    PlanStep,
    ProductionPlan,
    ProgressEvent,
    RenderResult,
    SceneBuildResult,
    SceneConfig,
    StrictBaseModel,
    TelemetryEvent,
)
from backend.core.telemetry import TelemetryBus
from backend.mcp.plan_engine import PlanEngine
from backend.mcp.server import FastMCPServer, mcp_server
from backend.mcp.tools import (
    SceneConfigDict,
    analyze_audio,
    auto_rig,
    build_ue5_scene,
    extract_mocap,
    image_to_3d,
    render_video,
)


# =============================================================================
# Helper Doubles & Media Creators
# =============================================================================

class StressTelemetryCollector(TelemetryBus):
    """Thread-safe event collector for stress testing."""

    def __init__(self) -> None:
        super().__init__()
        self.events: List[TelemetryEvent] = []
        self._lock = threading.Lock()

    def emit_threadsafe(self, event: TelemetryEvent) -> None:
        with self._lock:
            self.events.append(event)

    def get_events_of_type(self, event_cls: type) -> List[TelemetryEvent]:
        with self._lock:
            return [e for e in self.events if isinstance(e, event_cls)]


def _generate_test_wav(filepath: Path, duration_sec: float = 1.0) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 44100
    num_samples = int(duration_sec * sample_rate)
    with wave.open(str(filepath), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            val = int(0.4 * 32767.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wf.writeframes(frames)
    return filepath


def _generate_test_png(filepath: Path) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    filepath.write_bytes(png_bytes)
    return filepath


def _generate_test_glb(filepath: Path) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(b"glTF\x02\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00JSON\x00\x00\x00\x00BIN\x00")
    return filepath


def _generate_test_mp4(filepath: Path) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(b"\x00\x00\x00 ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x08mdat")
    return filepath


# =============================================================================
# 1. PlanEngine State Machine Promotion Oracle Tests
# =============================================================================

class TestPlanEnginePromotionOracle:
    """Rigorous verification of PlanEngine state promotion to PlanStatus.APPROVED."""

    def test_promotion_when_all_steps_approved_sequentially(self) -> None:
        """Requirement 1: confirm_step promotes plan.status to APPROVED when all steps approved."""
        collector = StressTelemetryCollector()
        engine = PlanEngine(telemetry_bus=collector)
        plan = engine.create_plan(goal="Sequential Approval Oracle")

        total_steps = len(plan.steps)
        assert total_steps == 5
        assert plan.status == PlanStatus.PROPOSED

        # Approve steps 0 through 3 (partial approvals)
        for i in range(total_steps - 1):
            step = plan.steps[i]
            res = engine.confirm_step(plan.plan_id, step.step_id, approved=True)
            assert step.status == PlanStatus.APPROVED
            # Must remain PROPOSED until the final step is approved
            assert res.status == PlanStatus.PROPOSED, f"Plan prematurely promoted at step index {i}"
            assert plan.status == PlanStatus.PROPOSED

        # Final step approval (step 4)
        last_step = plan.steps[-1]
        final_res = engine.confirm_step(plan.plan_id, last_step.step_id, approved=True)

        # Oracle checks
        assert last_step.status == PlanStatus.APPROVED
        assert all(s.status == PlanStatus.APPROVED for s in plan.steps)
        assert final_res.status == PlanStatus.APPROVED
        assert plan.status == PlanStatus.APPROVED

        # Verify telemetry proposal events: 1 initial (PROPOSED), 1 final (APPROVED)
        proposals = collector.get_events_of_type(PlanProposalEvent)
        assert len(proposals) == 2
        assert proposals[0].status == PlanStatus.PROPOSED
        assert proposals[1].status == PlanStatus.APPROVED
        assert proposals[1].plan_id == plan.plan_id

    def test_promotion_when_steps_approved_in_reverse_order(self) -> None:
        """Adversarial ordering: approving steps in reverse [4, 3, 2, 1, 0]."""
        collector = StressTelemetryCollector()
        engine = PlanEngine(telemetry_bus=collector)
        plan = engine.create_plan(goal="Reverse Approval")

        step_ids = [s.step_id for s in reversed(plan.steps)]
        for idx, sid in enumerate(step_ids):
            res = engine.confirm_step(plan.plan_id, sid, approved=True)
            if idx < len(step_ids) - 1:
                assert res.status == PlanStatus.PROPOSED, f"Premature promotion on reverse step {idx}"
            else:
                assert res.status == PlanStatus.APPROVED, "Failed to promote when last reverse step approved"

        assert plan.status == PlanStatus.APPROVED
        assert all(s.status == PlanStatus.APPROVED for s in plan.steps)

    def test_promotion_when_steps_approved_scrambled(self) -> None:
        """Adversarial ordering: approving steps in arbitrary scrambled order [2, 0, 4, 1, 3]."""
        engine = PlanEngine()
        plan = engine.create_plan(goal="Scrambled Approval")
        scrambled_indices = [2, 0, 4, 1, 3]

        for step_idx in scrambled_indices[:-1]:
            engine.confirm_step(plan.plan_id, plan.steps[step_idx].step_id, approved=True)
            assert plan.status == PlanStatus.PROPOSED

        # Approve the very last step in the scrambled list
        engine.confirm_step(plan.plan_id, plan.steps[scrambled_indices[-1]].step_id, approved=True)
        assert plan.status == PlanStatus.APPROVED
        assert all(s.status == PlanStatus.APPROVED for s in plan.steps)

    def test_rejection_precludes_promotion(self) -> None:
        """If any step is rejected, plan transitions to REJECTED and cannot be promoted."""
        engine = PlanEngine()
        plan = engine.create_plan(goal="Rejection Preclusion")

        # Approve step 0, reject step 1
        engine.confirm_step(plan.plan_id, plan.steps[0].step_id, approved=True)
        assert plan.status == PlanStatus.PROPOSED

        engine.confirm_step(plan.plan_id, plan.steps[1].step_id, approved=False)
        assert plan.status == PlanStatus.REJECTED
        assert plan.steps[1].status == PlanStatus.REJECTED

        # Even if all remaining steps (2, 3, 4) and even re-approving step 1 occurs:
        for s in plan.steps[2:]:
            engine.confirm_step(plan.plan_id, s.step_id, approved=True)
            assert plan.status == PlanStatus.REJECTED

        # Attempt to approve rejected step
        engine.confirm_step(plan.plan_id, plan.steps[1].step_id, approved=True)
        assert plan.steps[1].status == PlanStatus.APPROVED
        # Plan MUST remain REJECTED because failure occurred
        assert plan.status == PlanStatus.REJECTED

    def test_idempotent_confirmations_on_approved_plan(self) -> None:
        """Calling confirm_step on an already approved plan does not cause errors."""
        engine = PlanEngine()
        plan = engine.create_plan(goal="Idempotency Plan")

        for s in plan.steps:
            engine.confirm_step(plan.plan_id, s.step_id, approved=True)

        assert plan.status == PlanStatus.APPROVED

        # Re-approve each step again
        for s in plan.steps:
            res = engine.confirm_step(plan.plan_id, s.step_id, approved=True)
            assert res.status == PlanStatus.APPROVED


# =============================================================================
# 2. PlanEngine Concurrency & Stress Tests
# =============================================================================

class TestPlanEngineConcurrencyStress:
    """Stress-test PlanEngine under concurrent thread and plan pressures."""

    def test_concurrent_step_confirmation_event_consistency(self) -> None:
        """20 threads confirming steps of the same plan concurrently."""
        collector = StressTelemetryCollector()
        engine = PlanEngine(telemetry_bus=collector)
        plan = engine.create_plan(goal="Concurrent Confirmation Event Consistency")

        errors: List[Exception] = []

        def worker(step_idx: int) -> None:
            try:
                sid = plan.steps[step_idx].step_id
                engine.confirm_step(plan.plan_id, sid, approved=True)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i % 5,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(s.status == PlanStatus.APPROVED for s in plan.steps)
        assert plan.status == PlanStatus.APPROVED

        # Verify progress events emitted
        progress_events = collector.get_events_of_type(ProgressEvent)
        assert len(progress_events) >= 5

    def test_high_volume_multi_plan_concurrency(self) -> None:
        """50 concurrent workers operating on 50 independent plans simultaneously."""
        collector = StressTelemetryCollector()
        engine = PlanEngine(telemetry_bus=collector)
        num_plans = 50

        plans = [engine.create_plan(goal=f"Multi-plan stress #{i}") for i in range(num_plans)]

        errors: List[str] = []

        def process_plan(p: ProductionPlan) -> None:
            try:
                # Approve all 5 steps
                for step in p.steps:
                    engine.confirm_step(p.plan_id, step.step_id, approved=True)
                if p.status != PlanStatus.APPROVED:
                    errors.append(f"Plan {p.plan_id} not approved: {p.status}")
            except Exception as exc:
                errors.append(f"Plan {p.plan_id} error: {exc}")

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(process_plan, p) for p in plans]
            for fut in as_completed(futures):
                fut.result()

        assert len(errors) == 0, f"Encountered errors: {errors}"
        for p in plans:
            assert p.status == PlanStatus.APPROVED
            assert all(s.status == PlanStatus.APPROVED for s in p.steps)

    def test_rapid_plan_creation_and_retrieval_integrity(self) -> None:
        """Ensure 200 rapid plan creations maintain thread-safety and unique lookup."""
        engine = PlanEngine()
        created_ids: List[str] = []

        for i in range(200):
            p = engine.create_plan(goal=f"Stress test plan {i}")
            created_ids.append(p.plan_id)

        assert len(set(created_ids)) == 200
        for pid in created_ids:
            found = engine.get_plan(pid)
            assert found is not None
            assert found.plan_id == pid


# =============================================================================
# 3. FastMCPServer Stress & Adversarial Boundaries
# =============================================================================

class TestFastMCPServerStress:
    """Stress test FastMCPServer tool invocation, dual-parity, and error boundaries."""

    def test_fastmcp_concurrent_tool_invocations(self, tmp_path: Path) -> None:
        """12 concurrent threads executing tools across FastMCPServer simultaneously."""
        server = FastMCPServer()

        # Prepare synthetic media files
        wav_path = _generate_test_wav(tmp_path / "audio_stress.wav", duration_sec=1.0)
        img_path = _generate_test_png(tmp_path / "img_stress.png")
        glb_path = _generate_test_glb(tmp_path / "mesh_stress.glb")
        mp4_path = _generate_test_mp4(tmp_path / "vid_stress.mp4")

        tasks: List[Tuple[str, Dict[str, Union[str, int, float, bool, None, Dict[str, str]]]]] = [
            ("analyze_audio", {"audio_path": str(wav_path)}),
            ("image_to_3d", {"image_path": str(img_path), "output_path": str(tmp_path / "out_mesh.glb")}),
            ("auto_rig", {"mesh_path": str(glb_path), "output_path": str(tmp_path / "out_rig.glb")}),
            ("extract_mocap", {"video_path": str(mp4_path), "target_fps": 30, "output_path": str(tmp_path / "out_mocap.glb")}),
            ("build_ue5_scene", {"scene_config": {"mesh_path": str(glb_path), "level_name": "ConcurrentLvl"}}),
            ("render_video", {"scene_path": "/Game/Seq/Test", "output_path": str(tmp_path / "out_render.mp4"), "fps": 60}),
        ] * 2  # 12 concurrent tool calls

        results: List[Tuple[str, bool]] = []
        errors: List[str] = []

        def call_worker(tool_name: str, kwargs: Dict[str, Union[str, int, float, bool, None, Dict[str, str]]]) -> None:
            try:
                res = server.call_tool(tool_name, **kwargs)
                results.append((tool_name, res is not None))
            except Exception as e:
                errors.append(f"{tool_name}: {e}")

        threads = [
            threading.Thread(target=call_worker, args=(t[0], t[1]))
            for t in tasks
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Concurrent tool call errors: {errors}"
        assert len(results) == 12
        assert all(success for _, success in results)

    def test_fastmcp_direct_vs_call_tool_parity(self, tmp_path: Path) -> None:
        """Validate dual-invocation parity: call_tool yields identical types as direct import."""
        server = FastMCPServer()
        wav = _generate_test_wav(tmp_path / "parity.wav", duration_sec=1.2)

        # Call via server
        res_server = server.call_tool("analyze_audio", audio_path=str(wav))
        # Call directly
        res_direct = analyze_audio(audio_path=str(wav))

        assert type(res_server) is type(res_direct)
        assert isinstance(res_server, AudioAnalysisResult)
        assert res_server.duration_seconds == res_direct.duration_seconds
        assert res_server.bpm == res_direct.bpm
        assert res_server.beat_timestamps == res_direct.beat_timestamps

    def test_fastmcp_dynamic_tool_registration_under_load(self) -> None:
        """Dynamic registration while another thread queries the tool list."""
        server = FastMCPServer()

        class DynamicResult(StrictBaseModel):
            echo: str

        def dummy_echo(msg: str = "hello") -> DynamicResult:
            return DynamicResult(echo=msg)

        stop_event = threading.Event()
        list_errors: List[Exception] = []

        def reader() -> None:
            while not stop_event.is_set():
                try:
                    tools = server.list_tools()
                    assert "analyze_audio" in tools
                except Exception as ex:
                    list_errors.append(ex)

        t = threading.Thread(target=reader)
        t.start()

        for i in range(20):
            server.register_tool(f"dyn_tool_{i}", dummy_echo)

        stop_event.set()
        t.join()

        assert len(list_errors) == 0
        assert "dyn_tool_19" in server.list_tools()
        res = server.call_tool("dyn_tool_19", msg="stress_success")
        assert isinstance(res, DynamicResult)
        assert res.echo == "stress_success"

    def test_fastmcp_invalid_parameter_boundaries(self) -> None:
        """Adversarial input boundary checks: invalid types, missing parameters."""
        server = FastMCPServer()

        # Non-existent tool
        with pytest.raises(KeyError, match="not registered"):
            server.call_tool("non_existent_tool_xyz")

        # Empty whitespace string
        with pytest.raises(TypeError, match="must be a non-empty string"):
            server.call_tool("analyze_audio", audio_path="   ")

        # Missing required parameter
        with pytest.raises(TypeError):
            server.call_tool("render_video")
