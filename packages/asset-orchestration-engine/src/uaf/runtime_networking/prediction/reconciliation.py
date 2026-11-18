"""
UAF-81.83: Client-Server Desync Detection and Reconciliation Logic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from ..models.definition import DesyncError, Vec3, ensure_finite_float


@dataclass(frozen=True)
class ReconciliationResult:
    """Outcome of a reconciliation check between client prediction and server state."""
    reconciled: bool
    error_distance: float
    replayed_ticks: int
    final_properties: Dict[str, Any]


class ReconciliationManager:
    """
    Detects divergence between locally predicted state and server authoritative state,
    initiating replay and correction if divergence exceeds tolerance.
    """

    def __init__(self, position_tolerance: float = 0.05, max_acceptable_error: float = 50.0):
        self.position_tolerance = position_tolerance
        self.max_acceptable_error = max_acceptable_error

    def calculate_position_error(
        self,
        predicted_pos: Vec3,
        server_pos: Vec3,
    ) -> float:
        """Compute Euclidean error distance between predicted and authoritative position."""
        dx = predicted_pos[0] - server_pos[0]
        dy = predicted_pos[1] - server_pos[1]
        dz = predicted_pos[2] - server_pos[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        return ensure_finite_float(dist, "calculate_position_error")

    def evaluate_divergence(
        self,
        predicted_props: Dict[str, Any],
        server_props: Dict[str, Any],
    ) -> Tuple[bool, float]:
        """
        Check if predicted properties have diverged from server properties beyond tolerance.
        Returns (has_diverged, error_distance).
        """
        pred_pos = predicted_props.get("position")
        srv_pos = server_props.get("position")

        if pred_pos is not None and srv_pos is not None:
            if isinstance(pred_pos, (list, tuple)) and isinstance(srv_pos, (list, tuple)):
                err = self.calculate_position_error(tuple(pred_pos), tuple(srv_pos))
                if err > self.max_acceptable_error:
                    # Critical divergence that indicates illegal teleport or extreme cheat/desync
                    raise DesyncError(
                        f"Extreme divergence detected ({err:.2f} > max {self.max_acceptable_error:.2f})"
                    )
                return (err > self.position_tolerance, err)

        # Non-positional divergence check
        diverged = False
        for k, s_val in server_props.items():
            if k in predicted_props and predicted_props[k] != s_val:
                diverged = True
                break

        return (diverged, 0.0)
