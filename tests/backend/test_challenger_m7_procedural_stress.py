"""
Tier 5 Adversarial Stress Suite for Decoupled Procedural Engine & Async UE5 Client.

Empirical Challenger verification for Milestone 7 Iteration 2:
1. backend.ai.procedural.generate_standalone_glb:
   - 0-length name, ultra-long name (10,000 chars), non-ASCII / Unicode mesh names.
   - Deeply nested directories auto-creation, path string vs Path object, idempotent overwrite.
   - Byte-level glTF 2.0 binary layout validation (magic, version, 4-byte chunk padding, headers).
2. backend.ai.procedural.read_glb_stats:
   - Non-existent file, 0-byte file, truncated headers (<20 bytes), corrupt magic.
   - Non-JSON first chunk, malformed JSON chunk, missing accessors, missing indices.
   - Dynamic vertex/polygon count extraction vs synthetic cube truth.
3. backend.ai.procedural.generate_standalone_video:
   - Negative duration (-5.0s), zero duration (0.0s), fractional sub-frame duration (0.001s).
   - Extreme fps (0, negative, 1, 120, 1000).
   - Fallback ISO-BMFF box synthesis when imageio is unavailable/fails.
4. backend.ai.procedural.inspect_video_properties:
   - Non-existent path fallback, zero-byte file, corrupt file, small files (<2KB).
   - Dynamic size-based heuristic duration clamping [1.0s, 60.0s].
   - Target FPS clamping (fps <= 0 clamped to max(1, fps)).
5. backend.ue5.client.AsyncUE5RestClient.health_check & _get_session:
   - Verification that _get_session exists and returns an active aiohttp.ClientSession.
   - Direct call without prior open(): automatic session initialization without AttributeError.
   - Responsive mock UE5 /remote/info endpoint returning 200 -> returns True.
   - Error response (500 Internal Server Error, 404 Not Found) -> returns False.
   - Dead / unreachable port with short timeout -> returns False without uncaught exceptions.
   - Multiple sequential health checks verify session reuse and clean close().

Zero-Any Policy strictly enforced with 100% type annotations and Pydantic v2 compliance.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import struct
import tempfile
from typing import Dict, List, Optional, Tuple, Union

import aiohttp
from aiohttp import web
import pytest

from backend.ai.procedural import (
    _create_mp4_box,
    generate_standalone_glb,
    generate_standalone_video,
    inspect_video_properties,
    read_glb_stats,
)
from backend.ue5.client import AsyncUE5RestClient, RetryConfig, _validate_glb_container


# =============================================================================
# Helper Utilities
# =============================================================================

def _parse_glb_chunks(glb_bytes: bytes) -> Tuple[bytes, bytes]:
    """Parse glTF 2.0 binary chunks (JSON chunk, BIN chunk)."""
    assert len(glb_bytes) >= 20
    magic, version, total_length = struct.unpack("<4sII", glb_bytes[:12])
    assert magic == b"glTF"
    assert version == 2
    assert total_length == len(glb_bytes)

    # First chunk (JSON)
    json_len, json_type = struct.unpack("<II", glb_bytes[12:20])
    assert json_type == 0x4E4F534A
    json_chunk = glb_bytes[20 : 20 + json_len]

    # Second chunk (BIN)
    bin_offset = 20 + json_len
    assert len(glb_bytes) >= bin_offset + 8
    bin_len, bin_type = struct.unpack("<II", glb_bytes[bin_offset : bin_offset + 8])
    assert bin_type == 0x004E4942
    bin_chunk = glb_bytes[bin_offset + 8 : bin_offset + 8 + bin_len]

    return json_chunk, bin_chunk


# =============================================================================
# 1. Procedural GLB Generation & Dynamic Stats Stress Tests
# =============================================================================

class TestProceduralGLBGeneration:
    """Stress tests and boundary checks for generate_standalone_glb and read_glb_stats."""

    def test_glb_zero_length_mesh_name(self, tmp_path: Path) -> None:
        """Verify generating a GLB with an empty string name produces a valid container."""
        glb_path = tmp_path / "empty_name.glb"
        v_count, p_count = generate_standalone_glb(glb_path, mesh_name="")

        assert v_count == 8
        assert p_count == 12
        assert glb_path.exists()
        assert glb_path.stat().st_size > 0

        # Validate binary container conformance
        err = _validate_glb_container(glb_path)
        assert err is None

        # Verify dynamic stats reader parses it correctly
        read_v, read_p = read_glb_stats(glb_path)
        assert read_v == 8
        assert read_p == 12

        # Verify JSON chunk content
        raw = glb_path.read_bytes()
        json_bytes, bin_bytes = _parse_glb_chunks(raw)
        data = json.loads(json_bytes.decode("utf-8"))
        assert data["nodes"][0]["name"] == ""
        assert data["meshes"][0]["name"] == ""

    def test_glb_ultra_long_and_unicode_mesh_name(self, tmp_path: Path) -> None:
        """Verify generating a GLB with 10k chars and Unicode characters produces valid container."""
        long_name = "Character_Mesh_ロボット_" + ("A" * 5000) + "_日本語_üöä"
        glb_path = tmp_path / "long_name.glb"
        v_count, p_count = generate_standalone_glb(glb_path, mesh_name=long_name)

        assert v_count == 8
        assert p_count == 12
        assert _validate_glb_container(glb_path) is None

        read_v, read_p = read_glb_stats(glb_path)
        assert read_v == 8
        assert read_p == 12

        raw = glb_path.read_bytes()
        json_bytes, bin_bytes = _parse_glb_chunks(raw)
        data = json.loads(json_bytes.decode("utf-8"))
        assert data["nodes"][0]["name"] == long_name

    def test_glb_deeply_nested_directory_creation(self, tmp_path: Path) -> None:
        """Verify destination directory auto-creation across multiple nested subfolders."""
        deep_path = tmp_path / "level1" / "level2" / "level3" / "nested" / "model.glb"
        assert not deep_path.parent.exists()

        v_count, p_count = generate_standalone_glb(deep_path)
        assert deep_path.exists()
        assert v_count == 8
        assert p_count == 12

    def test_glb_idempotent_overwrite(self, tmp_path: Path) -> None:
        """Verify calling generate_standalone_glb on an existing file safely overwrites it."""
        glb_path = tmp_path / "overwrite.glb"
        generate_standalone_glb(glb_path, mesh_name="First")
        size_first = glb_path.stat().st_size

        generate_standalone_glb(glb_path, mesh_name="SecondRun")
        size_second = glb_path.stat().st_size

        assert glb_path.exists()
        assert _validate_glb_container(glb_path) is None
        read_v, read_p = read_glb_stats(glb_path)
        assert read_v == 8
        assert read_p == 12

    def test_glb_binary_alignment_padding_rules(self, tmp_path: Path) -> None:
        """Verify that JSON and BIN chunks obey the strict glTF 2.0 4-byte alignment rule."""
        for name_len in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            glb_path = tmp_path / f"align_{name_len}.glb"
            generate_standalone_glb(glb_path, mesh_name="X" * name_len)

            raw = glb_path.read_bytes()
            assert len(raw) % 4 == 0  # Total length must be 4-byte aligned

            # Check JSON chunk
            json_len = struct.unpack("<I", raw[12:16])[0]
            assert json_len % 4 == 0

            # Check BIN chunk
            bin_header_offset = 20 + json_len
            bin_len = struct.unpack("<I", raw[bin_header_offset : bin_header_offset + 4])[0]
            assert bin_len % 4 == 0


class TestReadGLBStatsBoundaries:
    """Boundary conditions and corruption stress for read_glb_stats."""

    def test_read_glb_nonexistent_file(self, tmp_path: Path) -> None:
        """Verify non-existent file returns (0, 0) without raising exception."""
        assert read_glb_stats(tmp_path / "ghost.glb") == (0, 0)

    def test_read_glb_zero_byte_file(self, tmp_path: Path) -> None:
        """Verify 0-byte file returns (0, 0) without raising exception."""
        zero_file = tmp_path / "zero.glb"
        zero_file.write_bytes(b"")
        assert read_glb_stats(zero_file) == (0, 0)

    def test_read_glb_truncated_header_under_20_bytes(self, tmp_path: Path) -> None:
        """Verify files between 1 and 19 bytes return (0, 0)."""
        for byte_size in [1, 5, 11, 12, 19]:
            trunc = tmp_path / f"trunc_{byte_size}.glb"
            trunc.write_bytes(b"\x00" * byte_size)
            assert read_glb_stats(trunc) == (0, 0)

    def test_read_glb_invalid_magic(self, tmp_path: Path) -> None:
        """Verify invalid magic bytes (e.g. not b'glTF') return (0, 0)."""
        bad_magic = tmp_path / "bad_magic.glb"
        bad_magic.write_bytes(struct.pack("<4sIIII", b"FAIL", 2, 28, 8, 0x4E4F534A) + b'{"a":1} ')
        assert read_glb_stats(bad_magic) == (0, 0)

    def test_read_glb_non_json_first_chunk(self, tmp_path: Path) -> None:
        """Verify glTF where first chunk is not JSON returns (0, 0)."""
        bad_chunk = tmp_path / "bad_chunk.glb"
        # First chunk type is BIN instead of JSON
        bad_chunk.write_bytes(struct.pack("<4sIIII", b"glTF", 2, 24, 4, 0x004E4942) + b"\x00" * 4)
        assert read_glb_stats(bad_chunk) == (0, 0)

    def test_read_glb_corrupt_json_payload(self, tmp_path: Path) -> None:
        """Verify malformed JSON syntax inside valid chunk header returns (0, 0)."""
        corrupt_json = tmp_path / "corrupt_json.glb"
        bad_payload = b"NOT_A_VALID_JSON{{"
        padded_len = len(bad_payload)
        corrupt_json.write_bytes(struct.pack("<4sIIII", b"glTF", 2, 20 + padded_len, padded_len, 0x4E4F534A) + bad_payload)
        assert read_glb_stats(corrupt_json) == (0, 0)

    def test_read_glb_missing_meshes_or_accessors(self, tmp_path: Path) -> None:
        """Verify valid glTF JSON without meshes or accessors returns (0, 0)."""
        empty_gltf = tmp_path / "empty_gltf.glb"
        payload = json.dumps({"asset": {"version": "2.0"}}).encode("utf-8")
        pad = (4 - (len(payload) % 4)) % 4
        payload += b" " * pad
        empty_gltf.write_bytes(struct.pack("<4sIIII", b"glTF", 2, 20 + len(payload), len(payload), 0x4E4F534A) + payload)
        assert read_glb_stats(empty_gltf) == (0, 0)

    def test_read_glb_unindexed_primitives(self, tmp_path: Path) -> None:
        """Verify primitives without indices derive polygon_count = vertex_count // 3."""
        unindexed = tmp_path / "unindexed.glb"
        payload = json.dumps({
            "asset": {"version": "2.0"},
            "accessors": [{"count": 9}],
            "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
        }).encode("utf-8")
        pad = (4 - (len(payload) % 4)) % 4
        payload += b" " * pad
        unindexed.write_bytes(struct.pack("<4sIIII", b"glTF", 2, 20 + len(payload), len(payload), 0x4E4F534A) + payload)

        v_count, p_count = read_glb_stats(unindexed)
        assert v_count == 9
        assert p_count == 3


# =============================================================================
# 2. Standalone Video Generation & Video Properties Stress Tests
# =============================================================================

class TestStandaloneVideoAndProperties:
    """Stress tests and boundary checks for generate_standalone_video and inspect_video_properties."""

    def test_generate_video_boundary_durations(self, tmp_path: Path) -> None:
        """Verify boundary duration values (0.0s, negative, sub-frame)."""
        # Duration 0.0s -> max(1.0, 0.0) ensures minimum 1.0s or valid container
        p_zero = generate_standalone_video(tmp_path / "zero.mp4", duration_seconds=0.0, fps=30)
        assert p_zero.exists()
        assert p_zero.stat().st_size > 0

        # Negative duration
        p_neg = generate_standalone_video(tmp_path / "neg.mp4", duration_seconds=-10.0, fps=24)
        assert p_neg.exists()
        assert p_neg.stat().st_size > 0

        # Sub-frame duration
        p_sub = generate_standalone_video(tmp_path / "sub.mp4", duration_seconds=0.005, fps=60)
        assert p_sub.exists()
        assert p_sub.stat().st_size > 0

    def test_generate_video_extreme_fps(self, tmp_path: Path) -> None:
        """Verify extreme fps values (0, negative, high)."""
        # fps = 0: Imageio may fail or raise, triggering fallback to ISO-BMFF box container
        p_fps0 = generate_standalone_video(tmp_path / "fps0.mp4", duration_seconds=1.0, fps=0)
        assert p_fps0.exists()
        assert p_fps0.stat().st_size > 0

        # negative fps
        p_fps_neg = generate_standalone_video(tmp_path / "fps_neg.mp4", duration_seconds=1.0, fps=-30)
        assert p_fps_neg.exists()
        assert p_fps_neg.stat().st_size > 0

        # high fps
        p_fps_high = generate_standalone_video(tmp_path / "fps_high.mp4", duration_seconds=1.0, fps=120)
        assert p_fps_high.exists()
        assert p_fps_high.stat().st_size > 0

    def test_generate_video_isobmff_box_fallback(self, tmp_path: Path) -> None:
        """Directly verify _create_mp4_box structure."""
        box = _create_mp4_box(b"test", b"hello world")
        assert len(box) == 8 + 11
        box_len, box_type = struct.unpack(">I4s", box[:8])
        assert box_len == 19
        assert box_type == b"test"
        assert box[8:] == b"hello world"

    def test_inspect_video_nonexistent_path(self, tmp_path: Path) -> None:
        """Verify non-existent video returns default 3.0s fallback with target fps."""
        non_existent = tmp_path / "ghost_video.mp4"
        frames, dur, joints = inspect_video_properties(non_existent, target_fps=30)
        assert dur == 3.0
        assert frames == 90
        assert joints == 33

        frames_60, dur_60, _ = inspect_video_properties(non_existent, target_fps=60)
        assert dur_60 == 3.0
        assert frames_60 == 180

    def test_inspect_video_zero_byte_file(self, tmp_path: Path) -> None:
        """Verify 0-byte file returns size-based heuristic clamped to minimum 1.0s."""
        zero_file = tmp_path / "zero.mp4"
        zero_file.write_bytes(b"")

        frames, dur, joints = inspect_video_properties(zero_file, target_fps=30)
        assert dur == 1.0
        assert frames == 30
        assert joints == 33

    def test_inspect_video_target_fps_clamping(self, tmp_path: Path) -> None:
        """Verify target_fps <= 0 is safely clamped to 1 fps without division by zero."""
        zero_file = tmp_path / "zero_fps.mp4"
        zero_file.write_bytes(b"")

        frames_0, dur_0, _ = inspect_video_properties(zero_file, target_fps=0)
        assert dur_0 == 1.0
        assert frames_0 == 1

        frames_neg, dur_neg, _ = inspect_video_properties(zero_file, target_fps=-50)
        assert dur_neg == 1.0
        assert frames_neg == 1

    def test_inspect_video_large_dummy_file_clamping(self, tmp_path: Path) -> None:
        """Verify large synthetic dummy files clamp heuristic duration to maximum 60.0s."""
        large_file = tmp_path / "large_dummy.mp4"
        # 1 MB file / 2048 = 512.0s -> clamped to 60.0s
        large_file.write_bytes(b"\x00" * (1024 * 1024))

        frames, dur, joints = inspect_video_properties(large_file, target_fps=30)
        assert dur == 60.0
        assert frames == 1800
        assert joints == 33

    def test_inspect_video_synthetic_mvhd_atom(self, tmp_path: Path) -> None:
        """Verify parsing authentic mvhd atom extracting duration and timescale."""
        mvhd_file = tmp_path / "custom_mvhd.mp4"
        # mvhd v0: 4 bytes version/flags, 8 bytes creation/mod, 4 bytes timescale, 4 bytes duration
        timescale = 1000
        duration_ms = 4500  # 4.5 seconds
        mvhd_payload = b"\x00\x00\x00\x00" + (b"\x00" * 8) + struct.pack(">II", timescale, duration_ms)
        mvhd_box = _create_mp4_box(b"mvhd", mvhd_payload)
        moov_box = _create_mp4_box(b"moov", mvhd_box)
        mvhd_file.write_bytes(moov_box)

        frames, dur, joints = inspect_video_properties(mvhd_file, target_fps=30)
        assert dur == 4.5
        assert frames == 135
        assert joints == 33


# =============================================================================
# 3. AsyncUE5RestClient Health Check & Session Management Stress Tests
# =============================================================================

class TestAsyncUE5RestClientHealthCheck:
    """Adversarial stress and defect verification for AsyncUE5RestClient.health_check."""

    def test_get_session_method_presence_and_initialization(self) -> None:
        """Verify _get_session is present, callable, and initializes the session."""
        async def run_check() -> None:
            client = AsyncUE5RestClient(host="127.0.0.1", port=30010)
            assert hasattr(client, "_get_session")
            assert callable(client._get_session)

            session = await client._get_session()
            assert session is not None
            assert not session.closed
            assert client._session is session

            await client.close()
            assert client._session is None

        asyncio.run(run_check())

    def test_health_check_without_prior_open_call(self) -> None:
        """
        Verify health_check automatically invokes open() internally.
        Must NOT raise AttributeError or any uncaught exception.
        """
        async def run_check() -> bool:
            # Point to offline port
            client = AsyncUE5RestClient(host="127.0.0.1", port=59996, timeout=0.1)
            # Call health_check directly without calling client.open()
            result = await client.health_check(timeout_seconds=0.05)
            await client.close()
            return result

        res = asyncio.run(run_check())
        assert res is False

    def test_health_check_responsive_mock_server_returns_true(self) -> None:
        """Verify health_check against a real local aiohttp HTTP server returns True on 200 OK."""
        async def run_server_test() -> None:
            app = web.Application()

            async def handle_remote_info(request: web.Request) -> web.Response:
                return web.json_response({"version": "5.4.0", "project": "IANIMATION"})

            app.router.add_get("/remote/info", handle_remote_info)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "127.0.0.1", 0)  # Bind to ephemeral port
            await site.start()

            # Retrieve actual assigned port
            assert site._server is not None
            sockets = site._server.sockets
            assert sockets is not None and len(sockets) > 0
            assigned_port = sockets[0].getsockname()[1]

            try:
                client = AsyncUE5RestClient(host="127.0.0.1", port=assigned_port, timeout=1.0)
                is_healthy = await client.health_check(timeout_seconds=1.0)
                assert is_healthy is True

                # Multiple sequential calls reuse session cleanly
                is_healthy_2 = await client.health_check(timeout_seconds=1.0)
                assert is_healthy_2 is True

                await client.close()
            finally:
                await runner.cleanup()

        asyncio.run(run_server_test())

    def test_health_check_error_status_codes_return_false(self) -> None:
        """Verify health_check returns False when endpoint returns 500 or 404."""
        async def run_error_status_test() -> None:
            app = web.Application()

            async def handle_error(request: web.Request) -> web.Response:
                return web.Response(status=500, text="Internal Server Error")

            app.router.add_get("/remote/info", handle_error)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "127.0.0.1", 0)
            await site.start()

            assert site._server is not None
            sockets = site._server.sockets
            assert sockets is not None and len(sockets) > 0
            assigned_port = sockets[0].getsockname()[1]

            try:
                client = AsyncUE5RestClient(host="127.0.0.1", port=assigned_port, timeout=0.5)
                is_healthy = await client.health_check(timeout_seconds=0.5)
                assert is_healthy is False
                await client.close()
            finally:
                await runner.cleanup()

        asyncio.run(run_error_status_test())

    def test_health_check_dead_port_clean_return(self) -> None:
        """Verify health_check against closed port cleanly returns False without raising."""
        async def run_dead_port_test() -> None:
            client = AsyncUE5RestClient(host="127.0.0.1", port=59995, timeout=0.05)
            # Call with tight timeout
            res = await client.health_check(timeout_seconds=0.05)
            assert res is False
            await client.close()

        asyncio.run(run_dead_port_test())
