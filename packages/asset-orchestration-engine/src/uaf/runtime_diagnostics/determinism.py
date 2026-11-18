"""
Determinism Diagnostics & Binary Divergence Search for UAF-81.86.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from .core import SubsystemType


@dataclass
class DivergencePoint:
    divergence_frame: int
    entity_id: Optional[str] = None
    component_name: Optional[str] = None
    property_name: Optional[str] = None
    value_run_a: Any = None
    value_run_b: Any = None
    state_hash_a: str = ""
    state_hash_b: str = ""
    subsystem: SubsystemType = SubsystemType.GENERAL
    divergent_properties: List[str] = field(default_factory=list)

    @property
    def divergent_frame(self) -> int:
        return self.divergence_frame

    @property
    def run_a_hash(self) -> str:
        return self.state_hash_a

    @property
    def run_b_hash(self) -> str:
        return self.state_hash_b


class DeterminismDiagnosticEngine:
    """
    Compares two deterministic simulation runs, executes binary search to pinpoint
    the first diverging frame, and produces detailed entity/component state diffs.
    """

    @staticmethod
    def find_divergence_frame(
        run_a_hashes: Union[List[Tuple[int, str]], List[str]],
        run_b_hashes: Union[List[Tuple[int, str]], List[str]],
    ) -> Optional[int]:
        """
        Binary search on frame hashes to find the first divergence frame index.
        Accepts either List[Tuple[frame_idx, hash]] or List[hash].
        """
        if not run_a_hashes or not run_b_hashes:
            return None

        # Normalize to list of (index, hash)
        if isinstance(run_a_hashes[0], tuple):
            norm_a: List[Tuple[int, str]] = list(run_a_hashes)  # type: ignore
        else:
            norm_a = [(i, h) for i, h in enumerate(run_a_hashes)]  # type: ignore

        if isinstance(run_b_hashes[0], tuple):
            norm_b: List[Tuple[int, str]] = list(run_b_hashes)  # type: ignore
        else:
            norm_b = [(i, h) for i, h in enumerate(run_b_hashes)]  # type: ignore

        min_len = min(len(norm_a), len(norm_b))
        if min_len == 0:
            return None

        # Check if identical throughout
        if norm_a[min_len - 1][1] == norm_b[min_len - 1][1]:
            return None if len(norm_a) == len(norm_b) else min_len

        # Binary search for the first mismatch
        low = 0
        high = min_len - 1
        divergence_idx = high

        while low <= high:
            mid = (low + high) // 2
            if norm_a[mid][1] != norm_b[mid][1]:
                divergence_idx = mid
                high = mid - 1
            else:
                low = mid + 1

        return norm_a[divergence_idx][0]

    def diff_frame_states(
        self,
        state_a: Dict[str, Any],
        state_b: Dict[str, Any],
        frame_index: int = 0,
        hash_a: str = "",
        hash_b: str = "",
    ) -> List[DivergencePoint]:
        """Deep comparison between two simulation states at a given frame."""
        points: List[DivergencePoint] = []
        all_keys = set(state_a.keys()) | set(state_b.keys())

        def deep_diff_props(prefix: str, val_a: Any, val_b: Any) -> List[str]:
            diffs: List[str] = []
            if isinstance(val_a, dict) and isinstance(val_b, dict):
                for k in set(val_a.keys()) | set(val_b.keys()):
                    new_prefix = f"{prefix}.{k}" if prefix else k
                    diffs.extend(deep_diff_props(new_prefix, val_a.get(k), val_b.get(k)))
            elif val_a != val_b:
                diffs.append(prefix)
            return diffs

        for entity_id in sorted(all_keys):
            ea = state_a.get(entity_id)
            eb = state_b.get(entity_id)
            if ea != eb:
                divergent_props = deep_diff_props("", ea, eb)
                points.append(
                    DivergencePoint(
                        divergence_frame=frame_index,
                        entity_id=entity_id,
                        component_name=None,
                        property_name=divergent_props[0] if divergent_props else None,
                        value_run_a=ea,
                        value_run_b=eb,
                        state_hash_a=hash_a,
                        state_hash_b=hash_b,
                        subsystem=SubsystemType.GENERAL,
                        divergent_properties=divergent_props,
                    )
                )

        return points

    def diff_frame_state(
        self,
        frame: int,
        state_a: Dict[str, Any],
        state_b: Dict[str, Any],
        hash_a: str = "",
        hash_b: str = "",
    ) -> Optional[DivergencePoint]:
        diffs = self.diff_frame_states(state_a, state_b, frame_index=frame, hash_a=hash_a, hash_b=hash_b)
        return diffs[0] if diffs else None
