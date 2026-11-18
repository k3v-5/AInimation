"""
Project-Agnostic Storage Path Resolution for Asset Orchestration Engine (AOE).
Ensures AOE remains completely decoupled and agnostic from specific projects, games,
hardcoded drive letters (e.g. E:\\), and local directory structures.
"""

import os
from pathlib import Path
from typing import Optional


def get_storage_root() -> Path:
    """
    Returns the storage root directory for the current project.
    Can be overridden via AOE_STORAGE_DIR or AOE_PROJECT_ROOT environment variables.
    Defaults to <workspace_root>/Saved.
    """
    override = os.environ.get("AOE_STORAGE_DIR")
    if override:
        return Path(override)

    project_root = os.environ.get("AOE_PROJECT_ROOT")
    if project_root:
        return Path(project_root) / "Saved"

    # Default to current working directory / Saved
    return Path(os.getcwd()) / "Saved"


def get_default_storage_path(subfolder: str, filename: str) -> str:
    """
    Returns a normalized, project-agnostic file path within the project storage directory.
    """
    root = get_storage_root()
    target_dir = root / subfolder
    return str(target_dir / filename)
