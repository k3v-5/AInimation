"""
Unit and Integration Tests for Blender Live Synchronization Bridge.

Validates:
- Wire protocol serialization (LiveCommand, LiveResponse, LiveSceneStatus).
- BlenderLiveClient connection timeout and failure handling.
- Mock server bidirectional communication (ping, set_frame, set_camera, set_lighting, get_status).
"""

import json
import socket
import threading
import time
import pytest

from backend.blender.live_bridge import (
    BlenderLiveClient,
    LiveCommand,
    LiveResponse,
    LiveSceneStatus,
)


def test_live_models_validation():
    """Verify live bridge wire protocol Pydantic models."""
    cmd = LiveCommand(action="set_frame", params={"frame": 42})
    assert cmd.action == "set_frame"
    assert cmd.params["frame"] == 42

    resp = LiveResponse(status="ok", message="Success", data={"key": "val"})
    assert resp.status == "ok"
    assert resp.data == {"key": "val"}

    status = LiveSceneStatus(
        active_camera="Camera_Main",
        current_frame=15,
        fps=30,
        objects=["Raven", "SunLight"],
        lights={"SunLight": 1000.0},
    )
    assert status.connected is True
    assert status.active_camera == "Camera_Main"
    assert status.current_frame == 15
    assert len(status.objects) == 2


def test_live_client_connection_refused():
    """Verify client gracefully handles server not running without unhandled crash."""
    client = BlenderLiveClient(host="127.0.0.1", port=59998, timeout=0.5)
    assert client.ping() is False
    assert client.get_status() is None
    assert client.set_frame(10) is False


def test_live_client_mock_bridge_communication():
    """
    Spin up a local TCP socket server emulating the Blender Addon bridge
    and verify BlenderLiveClient protocol transactions.
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", 0))
    port = server_sock.getsockname()[1]
    server_sock.listen(1)

    running = True

    def mock_server():
        server_sock.settimeout(2.0)
        while running:
            try:
                conn, _ = server_sock.accept()
                raw = conn.recv(4096).decode("utf-8").strip()
                if not raw:
                    conn.close()
                    continue
                cmd = json.loads(raw)
                action = cmd.get("action")

                if action == "ping":
                    resp = {"status": "ok", "message": "pong"}
                elif action == "get_status":
                    resp = {
                        "status": "ok",
                        "data": {
                            "connected": True,
                            "active_camera": "IANIMATION_Camera",
                            "camera_lens": 85.0,
                            "current_frame": 24,
                            "frame_start": 1,
                            "frame_end": 60,
                            "fps": 24,
                            "render_engine": "BLENDER_EEVEE_NEXT",
                            "objects": ["RedRaven3D", "AvianArmature"],
                            "lights": {"KeyLight": 550.0},
                        },
                    }
                elif action in ["set_frame", "set_camera", "set_lighting"]:
                    resp = {"status": "ok", "message": f"{action} applied"}
                else:
                    resp = {"status": "error", "message": "unknown action"}

                conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
                conn.close()
            except socket.timeout:
                continue
            except OSError:
                break

    thread = threading.Thread(target=mock_server, daemon=True)
    thread.start()

    try:
        client = BlenderLiveClient(host="127.0.0.1", port=port, timeout=1.5)
        # 1. Ping
        assert client.ping() is True

        # 2. Get Status
        status = client.get_status()
        assert status is not None
        assert status.active_camera == "IANIMATION_Camera"
        assert status.current_frame == 24
        assert "RedRaven3D" in status.objects

        # 3. Set Frame
        assert client.set_frame(35) is True

        # 4. Set Camera
        assert client.set_camera(location=(0, -5, 2), focal_length=100.0) is True

        # 5. Set Lighting
        assert client.set_lighting(key_energy=800.0, fill_energy=300.0) is True
    finally:
        running = False
        server_sock.close()
        thread.join(timeout=1.0)
