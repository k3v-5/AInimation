"""Asset registry maintaining multi-hash integrity and reference graphs."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class UE5AssetEntry:
    """Represents an asset registered and tracked in the Unreal Engine content space."""
    asset_id: str
    asset_type: str
    ue5_package_path: str
    source_hash: str
    content_hash: str
    build_hash: str
    revision: int = 1
    generation: int = 1
    is_loaded: bool = False
    dependencies: List[str] = field(default_factory=list)  # asset_ids this asset depends on
    referencers: List[str] = field(default_factory=list)   # asset_ids that reference this asset

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "ue5_package_path": self.ue5_package_path,
            "source_hash": self.source_hash,
            "content_hash": self.content_hash,
            "build_hash": self.build_hash,
            "revision": self.revision,
            "generation": self.generation,
            "is_loaded": self.is_loaded,
            "dependencies": list(self.dependencies),
            "referencers": list(self.referencers),
        }


class UE5AssetRegistry:
    """Manages asset references, build versions, and hot reload relinking."""

    def __init__(self) -> None:
        self._assets: Dict[str, UE5AssetEntry] = {}
        self._by_package_path: Dict[str, str] = {}

    @property
    def count(self) -> int:
        return len(self._assets)

    def register(
        self,
        entry_or_id: Optional[Union[UE5AssetEntry, str]] = None,
        ue5_package_path: str = "",
        asset_type: str = "",
        source_hash: str = "",
        content_hash: str = "",
        build_hash: str = "",
        dependencies: Optional[List[str]] = None,
        uaf_asset_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        **kwargs: Any,
    ) -> UE5AssetEntry:
        if isinstance(entry_or_id, UE5AssetEntry):
            entry = entry_or_id
        else:
            aid = uaf_asset_id or asset_id or (entry_or_id if isinstance(entry_or_id, str) else "")
            entry = UE5AssetEntry(
                asset_id=aid,
                asset_type=asset_type,
                ue5_package_path=ue5_package_path,
                source_hash=source_hash,
                content_hash=content_hash,
                build_hash=build_hash,
                dependencies=dependencies or [],
            )

        self._assets[entry.asset_id] = entry
        self._by_package_path[entry.ue5_package_path] = entry.asset_id

        # Update dependencies' referencers
        for dep_id in entry.dependencies:
            dep_entry = self._assets.get(dep_id)
            if dep_entry and entry.asset_id not in dep_entry.referencers:
                dep_entry.referencers.append(entry.asset_id)

        return entry

    def update_build_hash(self, asset_id: str, new_build_hash: str) -> UE5AssetEntry:
        entry = self._assets.get(asset_id)
        if not entry:
            raise KeyError(f"Asset '{asset_id}' not found in registry")
        entry.build_hash = new_build_hash
        entry.revision += 1
        return entry

    def get_dependents(self, asset_id: str) -> List[str]:
        return self.get_referencers(asset_id)

    def unregister(self, asset_id: str) -> Optional[UE5AssetEntry]:
        entry = self._assets.pop(asset_id, None)
        if entry:
            self._by_package_path.pop(entry.ue5_package_path, None)
        return entry

    def get(self, asset_id: str) -> Optional[UE5AssetEntry]:
        return self._assets.get(asset_id)

    def find_by_path(self, package_path: str) -> Optional[UE5AssetEntry]:
        aid = self._by_package_path.get(package_path)
        return self.get(aid) if aid else None

    def get_by_path(self, package_path: str) -> Optional[UE5AssetEntry]:
        return self.find_by_path(package_path)

    def add_reference(self, dependent_asset_id: str, referenced_asset_id: str) -> None:
        dep = self.get(dependent_asset_id)
        ref = self.get(referenced_asset_id)
        if dep and referenced_asset_id not in dep.dependencies:
            dep.dependencies.append(referenced_asset_id)
        if ref and dependent_asset_id not in ref.referencers:
            ref.referencers.append(dependent_asset_id)

    def get_referencers(self, asset_id: str) -> List[str]:
        entry = self.get(asset_id)
        return list(entry.referencers) if entry else []

    def get_all(self) -> List[UE5AssetEntry]:
        return list(self._assets.values())

    def clear(self) -> None:
        self._assets.clear()
        self._by_package_path.clear()
