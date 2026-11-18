"""
ProjectContext manages project roots and dynamic environment paths.
UAF-81.0 Sections 6, 7, 8, 47, 48.
Eliminates machine-specific hardcoded drive paths.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class ProjectContext:
    """
    Encapsulates all root paths and environment information for a project.
    Ensures complete path portability across platforms and file systems.
    """
    project_id: str
    project_root: Path
    workspace_root: Optional[Path] = None
    artifact_root: Optional[Path] = None
    cache_root: Optional[Path] = None
    output_root: Optional[Path] = None
    logs_root: Optional[Path] = None
    checkpoints_root: Optional[Path] = None
    temp_root: Optional[Path] = None
    environment_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.project_root = Path(self.project_root).resolve()
        
        # Derive defaults relative to project_root if not explicitly provided
        if self.workspace_root is None:
            self.workspace_root = self.project_root / "workspace"
        else:
            self.workspace_root = Path(self.workspace_root).resolve()

        if self.artifact_root is None:
            self.artifact_root = self.project_root / "artifacts"
        else:
            self.artifact_root = Path(self.artifact_root).resolve()

        if self.cache_root is None:
            self.cache_root = self.project_root / ".cache"
        else:
            self.cache_root = Path(self.cache_root).resolve()

        if self.output_root is None:
            self.output_root = self.project_root / "output"
        else:
            self.output_root = Path(self.output_root).resolve()

        if self.logs_root is None:
            self.logs_root = self.project_root / "logs"
        else:
            self.logs_root = Path(self.logs_root).resolve()

        if self.checkpoints_root is None:
            self.checkpoints_root = self.project_root / "checkpoints"
        else:
            self.checkpoints_root = Path(self.checkpoints_root).resolve()

        if self.temp_root is None:
            self.temp_root = self.project_root / ".tmp"
        else:
            self.temp_root = Path(self.temp_root).resolve()

    def ensure_directories(self) -> None:
        """Create all configured root directories if they do not exist."""
        for root in [
            self.project_root,
            self.workspace_root,
            self.artifact_root,
            self.cache_root,
            self.output_root,
            self.logs_root,
            self.checkpoints_root,
            self.temp_root,
        ]:
            if root:
                root.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_root": str(self.project_root),
            "workspace_root": str(self.workspace_root),
            "artifact_root": str(self.artifact_root),
            "cache_root": str(self.cache_root),
            "output_root": str(self.output_root),
            "logs_root": str(self.logs_root),
            "checkpoints_root": str(self.checkpoints_root),
            "temp_root": str(self.temp_root),
            "environment_metadata": self.environment_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectContext":
        return cls(
            project_id=data["project_id"],
            project_root=Path(data["project_root"]),
            workspace_root=Path(data["workspace_root"]) if data.get("workspace_root") else None,
            artifact_root=Path(data["artifact_root"]) if data.get("artifact_root") else None,
            cache_root=Path(data["cache_root"]) if data.get("cache_root") else None,
            output_root=Path(data["output_root"]) if data.get("output_root") else None,
            logs_root=Path(data["logs_root"]) if data.get("logs_root") else None,
            checkpoints_root=Path(data["checkpoints_root"]) if data.get("checkpoints_root") else None,
            temp_root=Path(data["temp_root"]) if data.get("temp_root") else None,
            environment_metadata=data.get("environment_metadata", {}),
        )

    @classmethod
    def discover(cls, start_path: Optional[Path] = None, project_id: str = "aoe_default") -> "ProjectContext":
        """
        Dynamically discover project root by walking upwards looking for marker files
        (e.g., pyproject.toml, .git, or AOE project configs) without relying on drive letters.
        """
        current = Path(start_path or Path.cwd()).resolve()
        markers = ["pyproject.toml", ".git", "uaf_project.json"]
        
        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return cls(project_id=project_id, project_root=current)
            current = current.parent

        # Fallback to current working directory
        return cls(project_id=project_id, project_root=Path.cwd().resolve())
