"""
UAF-81.101: Universal DCC & Engine Bridge Tools.
Provides project-agnostic, lightweight native tools and palettes
for Unreal Engine 5 (Python Editor Utility / Slate) and Blender (N-Panel Addons).
"""

from .core.contracts import (
    TargetEnvironment,
    ParameterType,
    ToolCategory,
    ToolParameterSpec,
    StudioActionSpec,
    ActionResult,
    EnginePaletteManifest,
    create_default_studio_actions,
)
from .ue5.palette_generator import UE5StudioPaletteGenerator
from .blender.panel_generator import BlenderStudioPanelGenerator
from .dispatch.action_dispatcher import StudioActionDispatcher

__all__ = [
    "TargetEnvironment",
    "ParameterType",
    "ToolCategory",
    "ToolParameterSpec",
    "StudioActionSpec",
    "ActionResult",
    "EnginePaletteManifest",
    "create_default_studio_actions",
    "UE5StudioPaletteGenerator",
    "BlenderStudioPanelGenerator",
    "StudioActionDispatcher",
]
