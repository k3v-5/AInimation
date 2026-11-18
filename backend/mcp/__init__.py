"""
FastMCP Package for IANIMATION.

Provides atomic tools, Human-in-the-Loop plan engine, and protocol server.
"""

from backend.mcp.plan_engine import PlanEngine
from backend.mcp.server import FastMCPServer, mcp_server, unified_mcp_server
from backend.mcp.tools import (
    analyze_audio,
    auto_rig,
    build_ue5_scene,
    extract_mocap,
    image_to_3d,
    list_monorepo_subsystems,
    render_video,
    search_monorepo_tools,
)
from backend.mcp.unified_registry import (
    SubsystemDomain,
    UnifiedAnimationRegistry,
    get_unified_registry,
)

__all__ = [
    "PlanEngine",
    "FastMCPServer",
    "mcp_server",
    "unified_mcp_server",
    "SubsystemDomain",
    "UnifiedAnimationRegistry",
    "get_unified_registry",
    "analyze_audio",
    "image_to_3d",
    "auto_rig",
    "extract_mocap",
    "build_ue5_scene",
    "render_video",
    "list_monorepo_subsystems",
    "search_monorepo_tools",
]
