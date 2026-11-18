"""
ArtifactLocation defines physical or virtual storage locations for artifacts.
UAF-81.0 Section 23.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class StorageBackend(str, Enum):
    FILESYSTEM = "FILESYSTEM"
    OBJECT_STORAGE = "OBJECT_STORAGE"
    DATABASE = "DATABASE"
    MEMORY = "MEMORY"


@dataclass(frozen=True)
class ArtifactLocation:
    """
    Representation of an artifact's storage destination.
    """
    backend: StorageBackend
    uri: str
    relative_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backend": self.backend.value,
            "uri": self.uri,
            "relative_path": self.relative_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactLocation":
        return cls(
            backend=StorageBackend(data.get("backend", "FILESYSTEM")),
            uri=data["uri"],
            relative_path=data.get("relative_path"),
        )
