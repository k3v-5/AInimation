"""Multi-run deterministic state hash and replay verifier."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DeterminismRunResult:
    run_id: str
    seed: int
    final_state_hash: str
    frame_hashes: List[str]
    event_count: int


@dataclass
class DeterminismComparisonReport:
    is_deterministic: bool
    runs_evaluated: int
    divergence_frame: Optional[int] = None
    state_hashes: List[str] = field(default_factory=list)
    message: str = ""


class DeterminismVerifier:
    """Verifies that multiple runs with identical seed and input produce identical state hashes."""

    def compare_runs(self, runs: List[DeterminismRunResult]) -> DeterminismComparisonReport:
        if not runs:
            return DeterminismComparisonReport(
                is_deterministic=False,
                runs_evaluated=0,
                message="No runs provided for determinism verification",
            )

        base_hash = runs[0].final_state_hash
        all_hashes = [r.final_state_hash for r in runs]

        # Check final hashes
        for idx, r in enumerate(runs[1:], start=1):
            if r.final_state_hash != base_hash:
                return DeterminismComparisonReport(
                    is_deterministic=False,
                    runs_evaluated=len(runs),
                    divergence_frame=len(r.frame_hashes),
                    state_hashes=all_hashes,
                    message=f"Final state hash mismatch between Run 0 ({base_hash[:8]}) and Run {idx} ({r.final_state_hash[:8]})",
                )

        # Check per-frame hash alignment
        min_frames = min(len(r.frame_hashes) for r in runs)
        for f in range(min_frames):
            frame_h = runs[0].frame_hashes[f]
            for idx, r in enumerate(runs[1:], start=1):
                if r.frame_hashes[f] != frame_h:
                    return DeterminismComparisonReport(
                        is_deterministic=False,
                        runs_evaluated=len(runs),
                        divergence_frame=f,
                        state_hashes=all_hashes,
                        message=f"Per-frame hash divergence at frame {f}",
                    )

        return DeterminismComparisonReport(
            is_deterministic=True,
            runs_evaluated=len(runs),
            state_hashes=all_hashes,
            message="All runs produced identical deterministic hashes",
        )
