"""
Blender 3D Engine Adapter for IANIMATION.

Implements Base3DEngineAdapter to orchestrate scene composition and high-fidelity rendering
using local Blender 4.3+ via headless execution and Python scripting (bpy).
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import List, Optional

from backend.core.models import RenderResult, SceneBuildResult, SceneConfig
from backend.engines.base import Base3DEngineAdapter


class BlenderAdapter(Base3DEngineAdapter):
    """
    Adapter for Blender 4.3+ automation.
    Supports headless scene building, Cycles/Eevee Next studio lighting, and video/still rendering.
    """

    def __init__(self, blender_bin: Optional[str] = None) -> None:
        super().__init__(engine_name="blender")
        self.blender_bin: str = self._resolve_blender_binary(blender_bin)
        self.scripts_dir: Path = Path(__file__).resolve().parent / "scripts"

    def _resolve_blender_binary(self, candidate: Optional[str] = None) -> str:
        """Resolve path to executable blender binary."""
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return str(Path(candidate).resolve())

        # Check local project symlink
        project_link = Path(__file__).resolve().parent.parent.parent / "blender"
        if project_link.is_file() and os.access(project_link, os.X_OK):
            return str(project_link.resolve())

        # Check system PATH
        which_blender = shutil.which("blender")
        if which_blender:
            return which_blender

        # Check common local install locations
        user_app = Path.home() / "Aplicaciones" / "blender" / "blender"
        if user_app.is_file() and os.access(user_app, os.X_OK):
            return str(user_app.resolve())

        # Check Windows common install locations
        win_candidates = [
            Path("E:/Blender/blender.exe"),
            Path("D:/Blender/blender.exe"),
            Path("C:/Blender/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 5.0/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.4/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
        ]
        for wc in win_candidates:
            if wc.is_file() and os.access(wc, os.X_OK):
                return str(wc.resolve())

        return "blender"

    def health_check(self) -> bool:
        """Check if Blender executable runs and reports valid version."""
        try:
            result = subprocess.run(
                [self.blender_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            return result.returncode == 0 and "Blender" in result.stdout
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            return False

    def build_scene(self, scene_config: SceneConfig) -> SceneBuildResult:
        """
        Build and save a .blend scene file incorporating the provided mesh, lighting, and camera.
        """
        output_blend = Path(f"outputs/scenes/{scene_config.level_name}.blend").resolve()
        output_blend.parent.mkdir(parents=True, exist_ok=True)

        render_script = self.scripts_dir / "studio_render.py"
        cmd: List[str] = [
            self.blender_bin,
            "-b",
            "-P",
            str(render_script),
            "--",
            "--output",
            str(output_blend.with_suffix(".png")),
            "--save-blend",
            str(output_blend),
        ]

        if scene_config.mesh_path:
            cmd.extend(["--mesh", str(Path(scene_config.mesh_path).resolve())])

        cmd.extend(["--samples", "16"])  # fast preview quality for scene setup

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                check=False,
            )
            success = res.returncode == 0 and output_blend.exists()
            msg = "Blender scene created successfully" if success else f"Build failed: {res.stderr}"
        except Exception as exc:
            success = False
            msg = f"Blender execution error: {str(exc)}"

        return SceneBuildResult(
            success=success,
            actor_ids=["Camera", "KeyLight", "FillLight", "RimLight", "SubjectMesh"],
            scene_path=str(output_blend),
            camera_actor_id="Camera",
            character_actor_id="SubjectMesh",
            message=msg,
        )

    def render_video(
        self,
        scene_path: str,
        output_path: str,
        fps: int = 60,
        resolution: str = "1920x1080",
        warmup_frames: int = 15,
        anti_aliasing_samples: int = 32,
    ) -> RenderResult:
        """
        Render final image or animation sequence using Cycles/Eevee Next via Blender CLI.
        """
        start_time = time.time()
        dest = Path(output_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)

        render_script = self.scripts_dir / "studio_render.py"
        mesh_arg = scene_path if Path(scene_path).suffix.lower() in [".glb", ".gltf", ".obj"] else None

        cmd: List[str] = [
            self.blender_bin,
            "-b",
            "-P",
            str(render_script),
            "--",
            "--output",
            str(dest),
            "--resolution",
            resolution,
            "--samples",
            str(anti_aliasing_samples),
            "--engine",
            "CYCLES",
        ]

        if mesh_arg:
            cmd.extend(["--mesh", str(Path(mesh_arg).resolve())])

        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
        elapsed = round(max(0.1, time.time() - start_time), 2)
        success = res.returncode == 0 and dest.exists()
        file_size = dest.stat().st_size if success else 0

        return RenderResult(
            video_path=str(dest),
            frame_count=1 if dest.suffix.lower() == ".png" else 60,
            elapsed_seconds=elapsed,
            fps=fps,
            resolution=resolution,
            file_size_bytes=file_size,
            success=success,
        )
