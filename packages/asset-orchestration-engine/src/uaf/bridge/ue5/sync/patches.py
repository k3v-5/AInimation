"""RFC 6902-style delta patching and state differential extraction."""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Union


class PatchOperation(str, Enum):
    REPLACE = "replace"
    ADD = "add"
    REMOVE = "remove"


@dataclass
class PatchRecord:
    """A single atomic property mutation."""
    object_id: str
    path: str  # e.g. "actor_01.x"
    op: PatchOperation
    value: Any = None
    old_value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_id": self.object_id,
            "path": self.path,
            "op": self.op.value,
            "value": self.value,
            "old_value": self.old_value,
        }


@dataclass
class StatePatch:
    """Represents a set of property mutations, backward-compatible with single-mutation usage."""
    operations: List[PatchRecord] = field(default_factory=list)
    object_id: str = "root"
    path: str = ""
    op: PatchOperation = PatchOperation.REPLACE
    value: Any = None
    old_value: Any = None

    def __post_init__(self) -> None:
        # If instantiated with single op arguments, ensure it's in operations
        if self.path and not self.operations:
            self.operations.append(
                PatchRecord(
                    object_id=self.object_id,
                    path=self.path,
                    op=self.op,
                    value=self.value,
                    old_value=self.old_value,
                )
            )

    def __len__(self) -> int:
        return len(self.operations)

    def __iter__(self) -> Iterator[PatchRecord]:
        return iter(self.operations)

    def __getitem__(self, index: int) -> PatchRecord:
        return self.operations[index]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operations": [op.to_dict() for op in self.operations],
            "object_id": self.object_id,
        }


def _apply_single_op(target: Dict[str, Any], op_record: PatchRecord) -> None:
    tokens = op_record.path.split(".")
    curr = target
    for token in tokens[:-1]:
        if token not in curr or not isinstance(curr[token], dict):
            curr[token] = {}
        curr = curr[token]

    last_token = tokens[-1]
    if op_record.op in (PatchOperation.REPLACE, PatchOperation.ADD):
        curr[last_token] = copy.deepcopy(op_record.value)
    elif op_record.op == PatchOperation.REMOVE:
        curr.pop(last_token, None)


def apply_patch(
    target: Dict[str, Any],
    patch: Union[StatePatch, PatchRecord, List[Union[StatePatch, PatchRecord]]],
) -> Dict[str, Any]:
    """Applies property patches to a dictionary and returns the updated state."""
    result = copy.deepcopy(target)
    if isinstance(patch, StatePatch):
        for op in patch.operations:
            _apply_single_op(result, op)
    elif isinstance(patch, PatchRecord):
        _apply_single_op(result, patch)
    elif isinstance(patch, list):
        for item in patch:
            if isinstance(item, StatePatch):
                for op in item.operations:
                    _apply_single_op(result, op)
            elif isinstance(item, PatchRecord):
                _apply_single_op(result, item)
    return result


def diff_dict(
    old_dict: Dict[str, Any],
    new_dict: Dict[str, Any],
    object_id: str = "root",
    prefix: str = "",
) -> StatePatch:
    """Recursively computes fine-grained property patches between two states."""
    records: List[PatchRecord] = []
    all_keys = set(old_dict.keys()) | set(new_dict.keys())

    for key in sorted(all_keys):
        path = f"{prefix}.{key}" if prefix else key
        in_old = key in old_dict
        in_new = key in new_dict

        if in_old and not in_new:
            records.append(
                PatchRecord(object_id=object_id, path=path, op=PatchOperation.REMOVE, value=None, old_value=old_dict[key])
            )
        elif not in_old and in_new:
            records.append(
                PatchRecord(object_id=object_id, path=path, op=PatchOperation.ADD, value=new_dict[key], old_value=None)
            )
        else:
            val_old = old_dict[key]
            val_new = new_dict[key]
            if isinstance(val_old, dict) and isinstance(val_new, dict):
                sub_patch = diff_dict(val_old, val_new, object_id=object_id, prefix=path)
                records.extend(sub_patch.operations)
            elif val_old != val_new:
                records.append(
                    PatchRecord(object_id=object_id, path=path, op=PatchOperation.REPLACE, value=val_new, old_value=val_old)
                )

    return StatePatch(operations=records, object_id=object_id)
