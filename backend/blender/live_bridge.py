"""
Blender Live Synchronization Bridge for IANIMATION.

Enables real-time, non-blocking bidirectional communication between IANIMATION
(Tauri UI / FastMCP / Python backend) and an active Blender instance via TCP JSON sockets.
"""

from __future__ import annotations

import json
import socket
import time
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class LiveSceneStatus(BaseModel):
    """Snapshot of current state in live Blender session."""

    connected: bool = True
    active_camera: Optional[str] = None
    camera_lens: float = 85.0
    current_frame: int = 1
    frame_start: int = 1
    frame_end: int = 250
    fps: int = 24
    render_engine: str = "BLENDER_EEVEE_NEXT"
    objects: List[str] = Field(default_factory=list)
    lights: Dict[str, float] = Field(default_factory=dict)


class LiveCommand(BaseModel):
    """Wire command sent to Blender Live Bridge."""

    action: str
    params: Dict[str, Any] = Field(default_factory=dict)


class LiveResponse(BaseModel):
    """Response returned by Blender Live Bridge."""

    status: str = "ok"
    message: str = ""
    data: Optional[Dict[str, Any]] = None


class BlenderLiveClient:
    """
    Client for interacting with live Blender viewport session over local socket.
    Strictly typed, timeout-protected, and non-blocking.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 30030, timeout: float = 2.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_command(self, action: str, params: Optional[Dict[str, Any]] = None) -> LiveResponse:
        """Send JSON command to Blender and parse response."""
        payload = LiveCommand(action=action, params=params or {}).model_dump()
        wire_data = json.dumps(payload).encode("utf-8") + b"\n"

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.host, self.port))
            sock.sendall(wire_data)

            response_bytes = b""
            while b"\n" not in response_bytes:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_bytes += chunk

            if not response_bytes:
                return LiveResponse(status="error", message="Empty response from Blender Live Bridge")

            raw_resp = json.loads(response_bytes.decode("utf-8").strip())
            return LiveResponse.model_validate(raw_resp)
        except (socket.timeout, ConnectionRefusedError, OSError) as exc:
            return LiveResponse(status="error", message=f"Connection failed: {str(exc)}")
        finally:
            try:
                sock.close()
            except OSError:
                pass

    def ping(self) -> bool:
        """Check if live Blender bridge is listening and responsive."""
        resp = self.send_command("ping")
        return resp.status == "ok"

    def get_status(self) -> Optional[LiveSceneStatus]:
        """Query live Blender scene metadata."""
        resp = self.send_command("get_status")
        if resp.status == "ok" and resp.data:
            return LiveSceneStatus.model_validate(resp.data)
        return None

    def set_frame(self, frame: int) -> bool:
        """Scrub active timeline in Blender."""
        resp = self.send_command("set_frame", {"frame": frame})
        return resp.status == "ok"

    def set_camera(
        self,
        location: Optional[Tuple[float, float, float]] = None,
        rotation_euler: Optional[Tuple[float, float, float]] = None,
        focal_length: Optional[float] = None,
    ) -> bool:
        """Adjust camera position, orientation, or lens."""
        params: Dict[str, Any] = {}
        if location is not None:
            params["location"] = list(location)
        if rotation_euler is not None:
            params["rotation_euler"] = list(rotation_euler)
        if focal_length is not None:
            params["focal_length"] = focal_length

        resp = self.send_command("set_camera", params)
        return resp.status == "ok"

    def set_lighting(
        self,
        key_energy: Optional[float] = None,
        fill_energy: Optional[float] = None,
        rim_energy: Optional[float] = None,
        preset: Optional[str] = None,
    ) -> bool:
        """Adjust light intensities or trigger lighting preset."""
        params: Dict[str, Any] = {}
        if key_energy is not None:
            params["key_energy"] = key_energy
        if fill_energy is not None:
            params["fill_energy"] = fill_energy
        if rim_energy is not None:
            params["rim_energy"] = rim_energy
        if preset is not None:
            params["preset"] = preset

        resp = self.send_command("set_lighting", params)
        return resp.status == "ok"
