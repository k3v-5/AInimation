"""
UAF-81.83: Delta State Difference Calculation and Snapshot Reconstruction.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from ..models.definition import (
    EntitySnapshot,
    NetworkEntityId,
)


@dataclass(frozen=True)
class EntityDelta:
    """Represents property changes, spawn, or destruction for an entity relative to baseline."""
    net_id: NetworkEntityId
    is_spawn: bool = False
    is_destroy: bool = False
    owner_id: Optional[str] = None
    changed_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeltaSnapshot:
    """A compact state diff between an acknowledged base tick and current target tick."""
    base_tick: int
    target_tick: int
    entity_deltas: Tuple[EntityDelta, ...]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize delta snapshot to dictionary."""
        deltas = []
        for d in self.entity_deltas:
            deltas.append({
                "ns": d.net_id.namespace,
                "val": d.net_id.value,
                "spawn": d.is_spawn,
                "destroy": d.is_destroy,
                "owner": d.owner_id,
                "props": d.changed_properties,
            })
        return {
            "base_tick": self.base_tick,
            "target_tick": self.target_tick,
            "deltas": deltas,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DeltaSnapshot:
        """Construct DeltaSnapshot from dictionary."""
        deltas: List[EntityDelta] = []
        for raw in data.get("deltas", []):
            deltas.append(
                EntityDelta(
                    net_id=NetworkEntityId(namespace=raw["ns"], value=raw["val"]),
                    is_spawn=raw.get("spawn", False),
                    is_destroy=raw.get("destroy", False),
                    owner_id=raw.get("owner"),
                    changed_properties=raw.get("props", {}),
                )
            )
        return cls(
            base_tick=data["base_tick"],
            target_tick=data["target_tick"],
            entity_deltas=tuple(deltas),
        )

    def encode(self) -> bytes:
        """Serialize to compact JSON bytes."""
        return json.dumps(self.to_dict(), separators=(",", ":")).encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> DeltaSnapshot:
        """Deserialize from binary bytes."""
        return cls.from_dict(json.loads(data.decode("utf-8")))


class DeltaCompressor:
    """Computes and applies delta diffs between confirmed client baseline and authoritative world state."""

    @staticmethod
    def compute_delta(
        base_tick: int,
        target_tick: int,
        baseline_state: Dict[NetworkEntityId, Dict[str, Any]],
        current_state: Dict[NetworkEntityId, Dict[str, Any]],
        entity_owners: Optional[Dict[NetworkEntityId, Optional[str]]] = None,
        relevant_entity_ids: Optional[Set[NetworkEntityId]] = None,
    ) -> DeltaSnapshot:
        """
        Compute minimal delta for entities that changed relative to baseline.
        If relevant_entity_ids is provided, only include entities in the relevant set.
        """
        owners = entity_owners or {}
        deltas: List[EntityDelta] = []

        active_current_ids = set(current_state.keys())
        if relevant_entity_ids is not None:
            active_current_ids = active_current_ids.intersection(relevant_entity_ids)

        baseline_ids = set(baseline_state.keys())

        # 1. Check destroyed or left-relevancy entities
        destroyed_ids = baseline_ids - active_current_ids
        for net_id in sorted(destroyed_ids, key=lambda i: (i.namespace, i.value)):
            deltas.append(
                EntityDelta(
                    net_id=net_id,
                    is_destroy=True,
                )
            )

        # 2. Check spawned and updated entities
        for net_id in sorted(active_current_ids, key=lambda i: (i.namespace, i.value)):
            curr_props = current_state[net_id]
            owner = owners.get(net_id)

            if net_id not in baseline_state:
                # Newly spawned or entered relevancy
                deltas.append(
                    EntityDelta(
                        net_id=net_id,
                        is_spawn=True,
                        owner_id=owner,
                        changed_properties=dict(curr_props),
                    )
                )
            else:
                # Existed in baseline, compute property diff
                base_props = baseline_state[net_id]
                changed = {}
                for k, v in curr_props.items():
                    if k not in base_props or base_props[k] != v:
                        changed[k] = v

                # Also check if properties were deleted
                for k in base_props:
                    if k not in curr_props:
                        changed[k] = None

                if changed:
                    deltas.append(
                        EntityDelta(
                            net_id=net_id,
                            is_spawn=False,
                            owner_id=owner,
                            changed_properties=changed,
                        )
                    )

        return DeltaSnapshot(
            base_tick=base_tick,
            target_tick=target_tick,
            entity_deltas=tuple(deltas),
        )

    @staticmethod
    def apply_delta(
        baseline_state: Dict[NetworkEntityId, Dict[str, Any]],
        delta: DeltaSnapshot,
    ) -> Dict[NetworkEntityId, Dict[str, Any]]:
        """Apply delta modifications to a baseline state copy, returning the updated state."""
        result = copy.deepcopy(baseline_state)

        for d in delta.entity_deltas:
            if d.is_destroy:
                result.pop(d.net_id, None)
            elif d.is_spawn:
                result[d.net_id] = copy.deepcopy(d.changed_properties)
            else:
                # Partial update
                if d.net_id not in result:
                    result[d.net_id] = {}
                ent_props = result[d.net_id]
                for k, v in d.changed_properties.items():
                    if v is None:
                        ent_props.pop(k, None)
                    else:
                        ent_props[k] = v

        return result
