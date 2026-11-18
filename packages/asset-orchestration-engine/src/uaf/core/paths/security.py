"""
Path Security Validator detects traversal attacks, unauthorized root access, and escapes.
UAF-81.0 Section 8.
"""

from pathlib import Path
from typing import Sequence


class PathSecurityViolation(Exception):
    """Raised when a path breaches security or sandboxing rules."""
    pass


class PathSecurityValidator:
    """
    Validates that a resolved path is strictly confined to one of the authorized roots.
    """
    @staticmethod
    def validate_traversal(relative_path: str) -> None:
        """Reject obvious traversal tokens before resolution."""
        normalized = str(relative_path).replace("\\", "/")
        parts = normalized.split("/")
        if ".." in parts:
            raise PathSecurityViolation(f"Path traversal detected in relative path: {relative_path}")

    @staticmethod
    def validate_confined_to_root(target_path: Path, allowed_root: Path) -> Path:
        """
        Verify that target_path is inside allowed_root.
        Returns the resolved target_path.
        """
        target_resolved = target_path.resolve()
        root_resolved = allowed_root.resolve()

        try:
            target_resolved.relative_to(root_resolved)
        except ValueError:
            raise PathSecurityViolation(
                f"Path escape detected: '{target_resolved}' is outside allowed root '{root_resolved}'."
            )
        return target_resolved

    @staticmethod
    def validate_within_roots(target_path: Path, allowed_roots: Sequence[Path]) -> Path:
        """Verify that target_path is inside at least one of the allowed roots."""
        target_resolved = target_path.resolve()
        for root in allowed_roots:
            try:
                target_resolved.relative_to(root.resolve())
                return target_resolved
            except ValueError:
                continue

        raise PathSecurityViolation(
            f"Path '{target_resolved}' is not within any authorized project roots."
        )
