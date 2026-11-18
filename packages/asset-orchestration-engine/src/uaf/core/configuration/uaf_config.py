"""
UAFConfig defines the unified hierarchical configuration tree.
UAF-81.0 Section 34.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class UAFConfig:
    """
    Centralized configuration dataclass covering all foundational engine domains.
    """
    project: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
    storage: Dict[str, Any] = field(default_factory=dict)
    cache: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    targets: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": self.project,
            "execution": self.execution,
            "storage": self.storage,
            "cache": self.cache,
            "logging": self.logging,
            "validation": self.validation,
            "targets": self.targets,
            "security": self.security,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UAFConfig":
        return cls(
            project=data.get("project", {}),
            execution=data.get("execution", {}),
            storage=data.get("storage", {}),
            cache=data.get("cache", {}),
            logging=data.get("logging", {}),
            validation=data.get("validation", {}),
            targets=data.get("targets", {}),
            security=data.get("security", {}),
        )

    @classmethod
    def create_default(cls) -> "UAFConfig":
        return cls(
            project={"name": "default_uaf_project", "version": "1.0.0"},
            execution={"deterministic": True, "seed": 42, "max_retries": 3},
            storage={"backend": "FILESYSTEM", "compression": "none"},
            cache={"enabled": True, "strategy": "content_hash"},
            logging={"level": "INFO", "structured": True},
            validation={"strict": True, "allow_unknown_fields": False},
            targets={"default": "generic", "supported": ["generic", "unreal", "blender"]},
            security={"sandbox_paths": True, "allow_symlinks": False},
        )
