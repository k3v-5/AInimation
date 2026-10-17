"""
Abstract 3D Engine Adapter Interface (Base3DEngineAdapter).

Defines the contract for DCC and game engine adapters (Unreal Engine 5, Blender, Godot)
following Clean Architecture, SOLID principles, and 100% strict typing (Zero-Any Policy).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models import RenderResult, SceneBuildResult, SceneConfig


class Base3DEngineAdapter(ABC):
    """
    Abstract interface for 3D engine integrations.
    Both Unreal Engine 5 and Blender adapters implement this contract interchangebly (LSP).
    """

    def __init__(self, engine_name: str) -> None:
        self.engine_name: str = engine_name

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the engine executable, daemon, or remote connection is healthy and responsive.
        """
        raise NotImplementedError

    @abstractmethod
    def build_scene(self, scene_config: SceneConfig) -> SceneBuildResult:
        """
        Assemble the 3D scene (mesh, lighting rig, camera trajectory, material parameters).
        """
        raise NotImplementedError

    @abstractmethod
    def render_video(
        self,
        scene_path: str,
        output_path: str,
        fps: int = 60,
        resolution: str = "1920x1080",
        warmup_frames: int = 15,
        anti_aliasing_samples: int = 8,
    ) -> RenderResult:
        """
        Render a final video or image sequence from the assembled scene.
        """
        raise NotImplementedError


def get_engine_adapter(engine: str = "blender") -> Base3DEngineAdapter:
    """
    Factory function to retrieve a concrete 3D engine adapter by name.

    Args:
        engine: 'blender', 'ue5', or 'unreal'.

    Returns:
        Base3DEngineAdapter instance.
    """
    eng = engine.lower().strip()
    if eng == "blender":
        from backend.blender.adapter import BlenderAdapter
        return BlenderAdapter()
    elif eng in ("ue5", "unreal", "unreal_engine"):
        from backend.ue5.adapter import UE5Adapter
        return UE5Adapter()
    else:
        raise ValueError(f"Unsupported 3D engine adapter: '{engine}'. Supported: 'blender', 'ue5'")
