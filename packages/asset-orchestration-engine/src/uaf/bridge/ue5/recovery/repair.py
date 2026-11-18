"""Orphan detection, reference relinking, and state repair engine."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set
from uaf.bridge.ue5.protocol.messages import SyncState
from uaf.bridge.ue5.registry.objects import UE5ObjectEntry, UE5ObjectRegistry
from uaf.bridge.ue5.registry.assets import UE5AssetRegistry


class OrphanPolicy(str, Enum):
    RECREATE = "RECREATE"
    DELETE = "DELETE"
    IMPORT = "IMPORT"
    QUARANTINE = "QUARANTINE"
    REPORT = "REPORT"


@dataclass
class OrphanReport:
    uaf_missing_in_ue: List[str] = field(default_factory=list)
    ue_missing_in_uaf: List[str] = field(default_factory=list)
    repaired_objects: List[str] = field(default_factory=list)
    quarantined_objects: List[str] = field(default_factory=list)

    @property
    def orphan_count(self) -> int:
        return len(self.uaf_missing_in_ue) + len(self.ue_missing_in_uaf)

    @property
    def orphaned_paths(self) -> List[str]:
        return list(self.ue_missing_in_uaf)


class BridgeRepairEngine:
    """Detects orphans and executes repair policies."""

    def __init__(
        self,
        registry: UE5ObjectRegistry,
        asset_registry: Optional[UE5AssetRegistry] = None,
        policy: OrphanPolicy = OrphanPolicy.REPORT,
    ) -> None:
        self.registry = registry
        self.asset_registry = asset_registry
        self.policy = policy

    def detect_orphans(
        self,
        known_ue_paths: Optional[Iterable[str]] = None,
        known_uaf_ids: Optional[Iterable[str]] = None,
        **kwargs: Any,
    ) -> OrphanReport:
        report = OrphanReport()
        ue_paths_set: Set[str] = set(known_ue_paths or [])
        uaf_ids_set: Set[str] = set(known_uaf_ids or [])

        all_entries = self.registry.get_all()
        # Handle dict or list returned by get_all()
        entry_list = list(all_entries.values()) if isinstance(all_entries, dict) else list(all_entries)

        for entry in entry_list:
            uaf_id = entry.uaf_object_id
            ue_path = entry.ue5_path

            # UAF exists in registry but not confirmed alive in UE5
            if ue_paths_set and ue_path not in ue_paths_set:
                report.uaf_missing_in_ue.append(uaf_id)
                entry.sync_state = SyncState.ORPHANED

        # UE5 object paths not mapped in registry
        for path in ue_paths_set:
            if not self.registry.find_by_path(path):
                report.ue_missing_in_uaf.append(path)

        return report

    def apply_policy(self, report: OrphanReport, policy: Optional[OrphanPolicy] = None) -> None:
        active_policy = policy or self.policy
        if active_policy == OrphanPolicy.DELETE:
            for uaf_id in report.uaf_missing_in_ue:
                self.registry.unregister(uaf_id)
                report.repaired_objects.append(uaf_id)
        elif active_policy == OrphanPolicy.QUARANTINE:
            for uaf_id in report.uaf_missing_in_ue:
                entry = self.registry.resolve(uaf_id)
                if entry:
                    entry.sync_state = SyncState.CONFLICT
                    report.quarantined_objects.append(uaf_id)
