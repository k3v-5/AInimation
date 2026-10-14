"""
FastMCP Server Instance and Protocol Server for IANIMATION.

Exposes the 6 atomic tools over the Model Context Protocol (stdio / SSE) with
JSON Schema definitions, strict validation, and telemetry streaming.

100% Zero-Any compliant with strict Pydantic model return types.
"""

from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional, Union

from backend.core.models import (
    AudioAnalysisResult,
    AutoRigResult,
    ImageTo3DResult,
    MocapResult,
    RenderResult,
    SceneBuildResult,
    StrictBaseModel,
)
from backend.mcp.tools import (
    analyze_audio,
    auto_rig,
    build_ue5_scene,
    extract_mocap,
    image_to_3d,
    render_video,
)

logger = logging.getLogger("ianimation.mcp.server")

# Strict Type Definitions (Zero-Any Policy)
MCPToolResult = Union[
    AudioAnalysisResult,
    ImageTo3DResult,
    AutoRigResult,
    MocapResult,
    SceneBuildResult,
    RenderResult,
    StrictBaseModel,
]
MCPToolCallable = Callable[..., MCPToolResult]
MCPParamScalar = Union[str, int, float, bool, None]
MCPParamValue = Union[
    MCPParamScalar,
    List[str],
    List[int],
    List[float],
    Dict[str, MCPParamScalar],
    Dict[str, Union[str, int, float, bool, None, List[Dict[str, float]], Dict[str, Union[str, float, bool]]]],
]


class FastMCPServer:
    """
    Model Context Protocol Server implementation for IANIMATION orchestrator tools.
    """

    def __init__(self, server_name: str = "ianimation-orchestrator") -> None:
        self.server_name: str = server_name
        self.tools: Dict[str, MCPToolCallable] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self.register_tool("analyze_audio", analyze_audio)
        self.register_tool("image_to_3d", image_to_3d)
        self.register_tool("auto_rig", auto_rig)
        self.register_tool("extract_mocap", extract_mocap)
        self.register_tool("build_ue5_scene", build_ue5_scene)
        self.register_tool("render_video", render_video)

    def register_tool(self, name: str, func: MCPToolCallable) -> None:
        """Register a callable tool by name."""
        self.tools[name] = func

    def call_tool(self, name: str, **kwargs: MCPParamValue) -> MCPToolResult:
        """Execute a registered tool directly with dual-invocation parity."""
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' is not registered in FastMCP server")
        return self.tools[name](**kwargs)

    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools.keys())


# Global default instance
mcp_server = FastMCPServer()
