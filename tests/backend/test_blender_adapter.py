"""
Unit and Integration tests for BlenderAdapter and Base3DEngineAdapter.

Verifies:
- SOLID contract compliance (Base3DEngineAdapter LSP)
- Blender 4.3+ binary discovery and health check
- Headless scene construction
- Studio render execution producing valid image files
"""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from backend.blender.adapter import BlenderAdapter
from backend.core.models import RenderResult, SceneBuildResult, SceneConfig
from backend.engines.base import Base3DEngineAdapter


@pytest.fixture
def adapter() -> BlenderAdapter:
    return BlenderAdapter()


def test_blender_adapter_implements_base_interface(adapter: BlenderAdapter) -> None:
    """Validate that BlenderAdapter conforms to Base3DEngineAdapter (LSP/DIP)."""
    assert isinstance(adapter, Base3DEngineAdapter)
    assert adapter.engine_name == "blender"


def test_blender_adapter_health_check(adapter: BlenderAdapter) -> None:
    """Validate health check against local installed Blender binary."""
    assert adapter.health_check() is True


def test_blender_adapter_build_scene(adapter: BlenderAdapter, tmp_path: Path) -> None:
    """Validate programmatic scene building producing .blend file."""
    config = SceneConfig(
        mesh_path="sample_mesh.glb",
        level_name="test_blender_level",
    )
    result = adapter.build_scene(config)
    assert isinstance(result, SceneBuildResult)
    assert result.success is True
    assert Path(result.scene_path).exists()
    assert result.camera_actor_id == "Camera"


def test_blender_adapter_render(adapter: BlenderAdapter, tmp_path: Path) -> None:
    """Validate render execution outputting PNG image."""
    out_file = tmp_path / "test_render.png"
    result = adapter.render_video(
        scene_path="",
        output_path=str(out_file),
        resolution="640x360",
        anti_aliasing_samples=16,
    )
    assert isinstance(result, RenderResult)
    assert result.success is True
    assert out_file.exists()
    assert out_file.stat().st_size > 0


def test_engine_adapter_factory() -> None:
    """Validate factory function returns correct adapter subclasses."""
    from backend.engines.base import get_engine_adapter
    from backend.ue5.adapter import UE5Adapter

    blender_eng = get_engine_adapter("blender")
    assert isinstance(blender_eng, BlenderAdapter)

    ue5_eng = get_engine_adapter("ue5")
    assert isinstance(ue5_eng, UE5Adapter)


def test_tools_build_scene_dispatch() -> None:
    """Validate FastMCP tools.build_scene dispatches correctly to blender and ue5."""
    from backend.mcp.tools import build_scene, build_ue5_scene

    config = SceneConfig(mesh_path="sample_mesh.glb", level_name="stage_dispatch_test")
    
    # Test blender dispatch
    blender_res = build_scene(config, engine="blender")
    assert blender_res.success is True
    assert ".blend" in blender_res.scene_path

    # Test ue5 dispatch (mock/offline fallback)
    ue5_res = build_scene(config, engine="ue5")
    assert ue5_res.success is True
    assert "/Game/Sequences" in ue5_res.scene_path

    # Test backward-compatible alias
    alias_res = build_ue5_scene(config)
    assert alias_res.success is True
    assert "/Game/Sequences" in alias_res.scene_path

