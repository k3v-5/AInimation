"""Protocol versioning and handshake compatibility verification."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Tuple


class VersionMismatchError(Exception):
    """Raised when bridge protocol versions are fundamentally incompatible."""
    pass


@dataclass(frozen=True)
class BridgeProtocolVersion:
    major: int = 1
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, version_str: str) -> BridgeProtocolVersion:
        parts = version_str.strip().split(".")
        try:
            maj = int(parts[0]) if len(parts) > 0 else 1
            mn = int(parts[1]) if len(parts) > 1 else 0
            pt = int(parts[2]) if len(parts) > 2 else 0
            return cls(major=maj, minor=mn, patch=pt)
        except (ValueError, IndexError):
            return cls(1, 0, 0)

    def is_compatible_with(self, other: BridgeProtocolVersion) -> bool:
        # Strict major version compatibility
        if self.major != other.major:
            return False
        return True

    def is_compatible(self, other: BridgeProtocolVersion) -> bool:
        return self.is_compatible_with(other)

    def assert_compatible(self, other: BridgeProtocolVersion) -> None:
        if not self.is_compatible(other):
            raise VersionMismatchError(
                f"Protocol version mismatch: {self} is incompatible with {other}"
            )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def to_dict(self) -> Dict[str, int]:
        return {"major": self.major, "minor": self.minor, "patch": self.patch}


CURRENT_BRIDGE_PROTOCOL_VERSION = BridgeProtocolVersion(1, 0, 0)


@dataclass
class HandshakeResult:
    is_success: bool
    protocol_version: BridgeProtocolVersion
    engine_version: str
    error_message: str = ""
    session_id: str = ""
