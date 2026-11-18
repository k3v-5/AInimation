"""State determinism and projection verification between UAF and UE5."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uaf.bridge.ue5.sync.snapshots import BridgeSnapshot
from uaf.bridge.ue5.sync.patches import StatePatch, apply_patch


@dataclass
class DivergenceDetail:
    """Details of a single diverged property or object."""
    object_id: str
    property_path: str
    uaf_value: Any
    ue5_value: Any


@dataclass
class StateDivergenceReport:
    """Report on determinism and state alignment between UAF and UE5."""
    is_deterministic: bool
    uaf_state_hash: str
    ue5_state_hash: str
    divergences: List[DivergenceDetail] = field(default_factory=list)
    diverged_objects_count: int = 0


class DeterminismChecker:
    """Validates that UAF state and UE5 projected state maintain deterministic equivalence."""

    def compare_snapshots(
        self,
        uaf_snapshot: BridgeSnapshot,
        ue5_snapshot: BridgeSnapshot,
    ) -> StateDivergenceReport:
        """Compares two snapshots and reports state divergences."""
        divergences: List[DivergenceDetail] = []
        all_obj_ids = set(uaf_snapshot.objects.keys()) | set(ue5_snapshot.objects.keys())

        for obj_id in sorted(all_obj_ids):
            uaf_obj = uaf_snapshot.objects.get(obj_id)
            ue5_obj = ue5_snapshot.objects.get(obj_id)

            if uaf_obj is None:
                divergences.append(
                    DivergenceDetail(
                        object_id=obj_id,
                        property_path="<root>",
                        uaf_value=None,
                        ue5_value="present_in_ue5_only",
                    )
                )
                continue
            if ue5_obj is None:
                divergences.append(
                    DivergenceDetail(
                        object_id=obj_id,
                        property_path="<root>",
                        uaf_value="present_in_uaf_only",
                        ue5_value=None,
                    )
                )
                continue

            # Compare keys
            all_keys = set(uaf_obj.keys()) | set(ue5_obj.keys())
            for key in sorted(all_keys):
                u_val = uaf_obj.get(key)
                e_val = ue5_obj.get(key)
                if u_val != e_val:
                    divergences.append(
                        DivergenceDetail(
                            object_id=obj_id,
                            property_path=key,
                            uaf_value=u_val,
                            ue5_value=e_val,
                        )
                    )

        diverged_ids = {d.object_id for d in divergences}
        is_deterministic = len(divergences) == 0 and uaf_snapshot.state_hash == ue5_snapshot.state_hash

        return StateDivergenceReport(
            is_deterministic=is_deterministic,
            uaf_state_hash=uaf_snapshot.state_hash,
            ue5_state_hash=ue5_snapshot.state_hash,
            divergences=divergences,
            diverged_objects_count=len(diverged_ids),
        )

    def verify_patch_determinism(
        self,
        base_state: Dict[str, Any],
        patches: List[StatePatch],
        expected_final_hash: str,
    ) -> bool:
        """Applies patches in sequence and verifies that the resulting state matches expected hash."""
        current = dict(base_state)
        for patch in patches:
            current = apply_patch(current, patch)
        final_snapshot = BridgeSnapshot(frame=0, timestamp_us=0, objects=current)
        return final_snapshot.state_hash == expected_final_hash
