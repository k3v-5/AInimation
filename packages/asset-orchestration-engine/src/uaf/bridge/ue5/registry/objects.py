"""Stable object registry mapping universal IDs to UE5 actor paths and instances."""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from uaf.bridge.ue5.protocol.messages import AuthorityModel, SyncState
from uaf.bridge.ue5.sync.revisions import RevisionVector


@dataclass
class UE5ObjectEntry:
    """Registered binding between a logical UAF object and an Unreal Actor / UObject."""
    uaf_object_id: str
    ue5_path: str
    actor_class: str
    actor_instance: Any = None
    revision: RevisionVector = field(default_factory=RevisionVector)
    authority: AuthorityModel = AuthorityModel.UAF_AUTHORITATIVE
    sync_state: SyncState = SyncState.SYNCED
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def ue5_object_path(self) -> str:
        return self.ue5_path

    @property
    def content_hash(self) -> str:
        raw = json.dumps(self.properties, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uaf_object_id": self.uaf_object_id,
            "ue5_path": self.ue5_path,
            "actor_class": self.actor_class,
            "revision": self.revision.to_dict(),
            "authority": self.authority.value,
            "sync_state": self.sync_state.value,
            "properties": self.properties,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class UE5ObjectRegistry:
    """Maintains bidirectional identity consistency between UAF and UE5."""

    def __init__(self) -> None:
        self._by_id: Dict[str, UE5ObjectEntry] = {}
        self._by_path: Dict[str, str] = {}  # ue5_path -> uaf_object_id

    @property
    def count(self) -> int:
        return len(self._by_id)

    def register(
        self,
        entry_or_id: Optional[Union[UE5ObjectEntry, str]] = None,
        ue5_path: str = "",
        ue5_object_path: str = "",
        actor_class: str = "",
        object_type: str = "",
        actor_instance: Any = None,
        authority: AuthorityModel = AuthorityModel.UAF_AUTHORITATIVE,
        sync_state: SyncState = SyncState.SYNCED,
        uaf_object_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> UE5ObjectEntry:
        if isinstance(entry_or_id, UE5ObjectEntry):
            entry = entry_or_id
        else:
            oid = uaf_object_id or (entry_or_id if isinstance(entry_or_id, str) else "")
            path = ue5_object_path or ue5_path
            cls_name = object_type or actor_class or "Actor"
            entry = UE5ObjectEntry(
                uaf_object_id=oid,
                ue5_path=path,
                actor_class=cls_name,
                actor_instance=actor_instance,
                authority=authority,
                sync_state=sync_state,
                properties=properties or {},
                tags=tags or [],
                metadata=metadata or {},
            )

        self._by_id[entry.uaf_object_id] = entry
        self._by_path[entry.ue5_path] = entry.uaf_object_id
        return entry

    def unregister(self, uaf_object_id: str) -> Optional[UE5ObjectEntry]:
        entry = self._by_id.pop(uaf_object_id, None)
        if entry:
            self._by_path.pop(entry.ue5_path, None)
        return entry

    def get(self, uaf_object_id: str) -> Optional[UE5ObjectEntry]:
        return self._by_id.get(uaf_object_id)

    def resolve(self, uaf_object_id: str) -> Optional[UE5ObjectEntry]:
        return self.get(uaf_object_id)

    def find_by_uaf_id(self, uaf_object_id: str) -> Optional[UE5ObjectEntry]:
        return self.resolve(uaf_object_id)

    def find_by_path(self, ue5_path: str) -> Optional[UE5ObjectEntry]:
        obj_id = self._by_path.get(ue5_path)
        return self.resolve(obj_id) if obj_id else None

    def get_all(self) -> Dict[str, UE5ObjectEntry]:
        return dict(self._by_id)

    def validate(self) -> List[str]:
        errors: List[str] = []
        for obj_id, entry in self._by_id.items():
            if not entry.ue5_path:
                errors.append(f"Object '{obj_id}' has missing or empty ue5_path")
            if not entry.actor_class:
                errors.append(f"Object '{obj_id}' has missing actor_class")
            mapped_id = self._by_path.get(entry.ue5_path)
            if mapped_id != obj_id:
                errors.append(f"Path collision or inconsistency for path '{entry.ue5_path}'")
        return errors

    def rebuild(self) -> None:
        self._by_path.clear()
        for entry in self._by_id.values():
            self._by_path[entry.ue5_path] = entry.uaf_object_id

    def clear(self) -> None:
        self._by_id.clear()
        self._by_path.clear()
