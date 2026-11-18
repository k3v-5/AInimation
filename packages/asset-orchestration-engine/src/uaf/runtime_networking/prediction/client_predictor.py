"""
UAF-81.83: Client-Side Movement Prediction and Reconciliation Replay.
"""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..models.definition import InputCommand, NetworkEntityId, Vec3
from .reconciliation import ReconciliationManager, ReconciliationResult


def default_movement_simulation(
    current_props: Dict[str, Any],
    input_cmd: InputCommand,
    dt: float = 1.0 / 60.0,
) -> Dict[str, Any]:
    """
    Standard deterministic movement simulation step.
    Applies input axes to position with velocity/speed calculation.
    """
    props = copy.deepcopy(current_props)
    pos = props.get("position", (0.0, 0.0, 0.0))
    speed = float(props.get("speed", 10.0))

    ax_x = input_cmd.axes[0] if len(input_cmd.axes) > 0 else 0.0
    ax_y = input_cmd.axes[1] if len(input_cmd.axes) > 1 else 0.0
    ax_z = input_cmd.axes[2] if len(input_cmd.axes) > 2 else 0.0

    # Compute new position
    new_x = pos[0] + ax_x * speed * dt
    new_y = pos[1] + ax_y * speed * dt
    new_z = pos[2] + ax_z * speed * dt

    props["position"] = (round(new_x, 4), round(new_y, 4), round(new_z, 4))
    props["velocity"] = (round(ax_x * speed, 4), round(ax_y * speed, 4), round(ax_z * speed, 4))
    return props


class ClientPredictor:
    """
    Executes client-side prediction for locally owned entities and performs
    authoritative reconciliation replay upon receiving server snapshots.
    """

    def __init__(
        self,
        net_id: NetworkEntityId,
        initial_props: Dict[str, Any],
        simulation_fn: Optional[Callable[[Dict[str, Any], InputCommand, float], Dict[str, Any]]] = None,
        reconciliation_manager: Optional[ReconciliationManager] = None,
    ):
        self.net_id = net_id
        self.simulation_fn = simulation_fn or default_movement_simulation
        self.reconciliation_manager = reconciliation_manager or ReconciliationManager()

        self.current_state: Dict[str, Any] = copy.deepcopy(initial_props)
        self.unacked_inputs: List[InputCommand] = []
        self.prediction_history: Dict[int, Dict[str, Any]] = {}  # seq -> predicted state

    def predict_input(self, cmd: InputCommand, dt: float = 1.0 / 60.0) -> Dict[str, Any]:
        """Apply input locally and record to prediction history."""
        self.current_state = self.simulation_fn(self.current_state, cmd, dt)
        self.unacked_inputs.append(cmd)
        self.prediction_history[cmd.sequence] = copy.deepcopy(self.current_state)
        return dict(self.current_state)

    def reconcile_with_server(
        self,
        server_state: Dict[str, Any],
        acked_sequence: int,
        dt: float = 1.0 / 60.0,
    ) -> ReconciliationResult:
        """
        Compare server state with historical prediction at acked_sequence.
        If diverged, rewind to server state and replay remaining unacked inputs.
        """
        # Find predicted state for this acked sequence
        pred_state = self.prediction_history.get(acked_sequence, self.current_state)
        diverged, error_dist = self.reconciliation_manager.evaluate_divergence(pred_state, server_state)

        # Prune inputs acknowledged by server
        self.unacked_inputs = [cmd for cmd in self.unacked_inputs if cmd.sequence > acked_sequence]

        # Prune older prediction history
        cutoff = acked_sequence - 120
        for seq in list(self.prediction_history.keys()):
            if seq <= acked_sequence or seq < cutoff:
                del self.prediction_history[seq]

        if not diverged:
            return ReconciliationResult(
                reconciled=False,
                error_distance=error_dist,
                replayed_ticks=0,
                final_properties=dict(self.current_state),
            )

        # Divergence detected: reset to authoritative server state and resimulate unacked inputs
        resim_state = copy.deepcopy(server_state)
        replayed_count = 0

        for cmd in self.unacked_inputs:
            resim_state = self.simulation_fn(resim_state, cmd, dt)
            self.prediction_history[cmd.sequence] = copy.deepcopy(resim_state)
            replayed_count += 1

        self.current_state = resim_state
        return ReconciliationResult(
            reconciled=True,
            error_distance=error_dist,
            replayed_ticks=replayed_count,
            final_properties=dict(self.current_state),
        )
