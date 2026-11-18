"""
UAFPathResolver handles deterministic, drive-agnostic path resolution for assets, artifacts, and cache.
UAF-81.0 Sections 7, 8.
"""

from pathlib import Path
from typing import Optional, Union
from ..context.project_context import ProjectContext
from .security import PathSecurityValidator, PathSecurityViolation


class UAFPathResolver:
    """
    Resolves virtual and relative path references relative to a ProjectContext.
    Guarantees sandboxing and root independence.
    """
    def __init__(self, project_context: ProjectContext):
        self.context = project_context

    @property
    def allowed_roots(self):
        roots = [
            self.context.project_root,
            self.context.workspace_root,
            self.context.artifact_root,
            self.context.cache_root,
            self.context.output_root,
            self.context.logs_root,
            self.context.checkpoints_root,
            self.context.temp_root,
        ]
        return [r for r in roots if r is not None]

    def resolve_artifact_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a path inside the artifact root."""
        PathSecurityValidator.validate_traversal(str(relative_path))
        target = (self.context.artifact_root / relative_path).resolve()
        return PathSecurityValidator.validate_confined_to_root(target, self.context.artifact_root)

    def resolve_cache_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a path inside the cache root."""
        PathSecurityValidator.validate_traversal(str(relative_path))
        target = (self.context.cache_root / relative_path).resolve()
        return PathSecurityValidator.validate_confined_to_root(target, self.context.cache_root)

    def resolve_output_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a path inside the output root."""
        PathSecurityValidator.validate_traversal(str(relative_path))
        target = (self.context.output_root / relative_path).resolve()
        return PathSecurityValidator.validate_confined_to_root(target, self.context.output_root)

    def resolve_workspace_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a path inside the workspace root."""
        PathSecurityValidator.validate_traversal(str(relative_path))
        target = (self.context.workspace_root / relative_path).resolve()
        return PathSecurityValidator.validate_confined_to_root(target, self.context.workspace_root)

    def resolve_checkpoint_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a path inside the checkpoint root."""
        PathSecurityValidator.validate_traversal(str(relative_path))
        target = (self.context.checkpoints_root / relative_path).resolve()
        return PathSecurityValidator.validate_confined_to_root(target, self.context.checkpoints_root)

    def resolve_temp_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a path inside the temp root."""
        PathSecurityValidator.validate_traversal(str(relative_path))
        target = (self.context.temp_root / relative_path).resolve()
        return PathSecurityValidator.validate_confined_to_root(target, self.context.temp_root)

    def validate_any(self, path: Union[str, Path]) -> Path:
        """Validate that any path is safely within the project's authorized roots."""
        p = Path(path).resolve()
        return PathSecurityValidator.validate_within_roots(p, self.allowed_roots)
