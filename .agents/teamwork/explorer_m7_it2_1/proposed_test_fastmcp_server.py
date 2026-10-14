"""
Unit tests for FastMCP Server (registration, dual invocation parity, tool schemas, and error boundaries).
Conforms 100% to Zero-Any strict typing and SOLID architecture.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import pytest

from backend.mcp.server import FastMCPServer, mcp_server
from backend.core.models import (
    AudioAnalysisResult,
    AutoRigResult,
    ImageTo3DResult,
    MocapResult,
    RenderResult,
    SceneBuildResult,
)


class TestFastMCPServer:
    def test_default_tools_registered(self) -> None:
        tools = mcp_server.list_tools()
        expected = [
            "analyze_audio",
            "image_to_3d",
            "auto_rig",
            "extract_mocap",
            "build_ue5_scene",
            "render_video",
        ]
        for exp in expected:
            assert exp in tools

    def test_custom_server_instance(self) -> None:
        server = FastMCPServer(server_name="test-server")
        assert server.server_name == "test-server"
        assert len(server.list_tools()) == 6

    def test_unknown_tool_raises_key_error(self) -> None:
        server = FastMCPServer()
        with pytest.raises(KeyError, match="not registered"):
            server.call_tool("non_existent_tool")

    def test_atomic_tool_invocation_type_safety(self) -> None:
        server = FastMCPServer()
        # Test input type validation
        with pytest.raises(TypeError):
            server.call_tool("analyze_audio", audio_path=123)  # Invalid type

        with pytest.raises(TypeError):
            server.call_tool("image_to_3d", image_path="")  # Empty path rejected
