"""Revision vectors and vector clock concurrency tracking."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass
class RevisionVector:
    """Tracks causal ordering of modifications across UAF and UE5."""
    uaf_revision: int = 0
    ue5_revision: int = 0
    logical_revision: int = 0

    def increment_uaf(self) -> RevisionVector:
        return RevisionVector(
            uaf_revision=self.uaf_revision + 1,
            ue5_revision=self.ue5_revision,
            logical_revision=self.logical_revision + 1,
        )

    def increment_ue(self) -> RevisionVector:
        return RevisionVector(
            uaf_revision=self.uaf_revision,
            ue5_revision=self.ue5_revision + 1,
            logical_revision=self.logical_revision + 1,
        )

    def is_newer_than(self, other: RevisionVector) -> bool:
        """Returns True if self is strictly causally after other."""
        ge = (self.uaf_revision >= other.uaf_revision and self.ue5_revision >= other.ue5_revision)
        gt = (self.uaf_revision > other.uaf_revision or self.ue5_revision > other.ue5_revision)
        return ge and gt

    def is_concurrent_with(self, other: RevisionVector) -> bool:
        """Returns True if neither vector dominates the other (concurrent edit conflict)."""
        return not self.is_newer_than(other) and not other.is_newer_than(self) and (self != other)

    def merge(self, other: RevisionVector) -> RevisionVector:
        return RevisionVector(
            uaf_revision=max(self.uaf_revision, other.uaf_revision),
            ue5_revision=max(self.ue5_revision, other.ue5_revision),
            logical_revision=max(self.logical_revision, other.logical_revision) + 1,
        )

    def to_dict(self) -> Dict[str, int]:
        return {
            "uaf_revision": self.uaf_revision,
            "ue5_revision": self.ue5_revision,
            "logical_revision": self.logical_revision,
        }
