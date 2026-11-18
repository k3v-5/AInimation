"""
AssetIdentity provides a stable, unique, and serializable identity for any asset.
UAF-81.0 Section 11.
"""

from dataclasses import dataclass
from typing import Dict, Any, Union
from .asset_types import AssetType


@dataclass(frozen=True)
class AssetIdentity:
    """
    Immutable identity model for assets.
    """
    asset_id: str
    asset_type: AssetType
    namespace: str = "default"
    version: str = "1.0.0"

    def __post_init__(self):
        if not self.asset_id or not self.asset_id.strip():
            raise ValueError("asset_id must be a non-empty string.")
        if isinstance(self.asset_type, str):
            object.__setattr__(self, "asset_type", AssetType.from_str(self.asset_type))

    @property
    def urn(self) -> str:
        """Uniform Resource Name representation."""
        return f"urn:uaf:{self.namespace}:{self.asset_type.value.lower()}:{self.asset_id}@{self.version}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "namespace": self.namespace,
            "version": self.version,
            "urn": self.urn,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetIdentity":
        return cls(
            asset_id=data["asset_id"],
            asset_type=AssetType.from_str(data.get("asset_type", "OTHER")),
            namespace=data.get("namespace", "default"),
            version=data.get("version", "1.0.0"),
        )
