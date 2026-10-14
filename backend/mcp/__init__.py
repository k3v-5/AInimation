"""
FastMCP Package for IANIMATION.

Provides atomic tools, Human-in-the-Loop plan engine, and protocol server.
"""

from backend.mcp.plan_engine import PlanEngine
from backend.mcp.server import FastMCPServer, mcp_server
from backend.mcp.tools import (
    analyze_audio,
    auto_rig,
    build_ue5_scene,
    extract_mocap,
    image_to_3d,
    render_video,
)

__all__ = [
    "PlanEngine",
    "FastMCPServer",
    "mcp_server",
    "analyze_audio",
    "image_to_3d",
    "auto_rig",
    "extract_mocap",
    "build_ue5_scene",
    "render_video",
]
