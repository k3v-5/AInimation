import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..core.golden_types import GoldenStatus, VersionBumpType

@dataclass
class GoldenVersion:
    major: int = 1
    minor: int = 0
    patch: int = 0

    def to_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_string(cls, v_str: str) -> "GoldenVersion":
        parts = v_str.strip().split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: '{v_str}'. Must be MAJOR.MINOR.PATCH")
        return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))

    def bump(self, bump_type: VersionBumpType) -> "GoldenVersion":
        if bump_type == VersionBumpType.MAJOR:
            return GoldenVersion(self.major + 1, 0, 0)
        elif bump_type == VersionBumpType.MINOR:
            return GoldenVersion(self.major, self.minor + 1, 0)
        else: # PATCH
            return GoldenVersion(self.major, self.minor, self.patch + 1)

@dataclass
class GoldenVersionInfo:
    version_str: str
    parent_version: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    created_by: str = "agent.strategy"
    content_hash: str = ""
    manifest_hash: str = ""
    baseline_id: str = ""
    evaluation_id: str = ""
    status: GoldenStatus = GoldenStatus.GOLDEN
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_str": self.version_str,
            "parent_version": self.parent_version,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "content_hash": self.content_hash,
            "manifest_hash": self.manifest_hash,
            "baseline_id": self.baseline_id,
            "evaluation_id": self.evaluation_id,
            "status": self.status.value,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoldenVersionInfo":
        return cls(
            version_str=data["version_str"],
            parent_version=data.get("parent_version"),
            created_at=data.get("created_at", time.time()),
            created_by=data.get("created_by", "agent.strategy"),
            content_hash=data.get("content_hash", ""),
            manifest_hash=data.get("manifest_hash", ""),
            baseline_id=data.get("baseline_id", ""),
            evaluation_id=data.get("evaluation_id", ""),
            status=GoldenStatus(data.get("status", "GOLDEN")),
            notes=data.get("notes", "")
        )
