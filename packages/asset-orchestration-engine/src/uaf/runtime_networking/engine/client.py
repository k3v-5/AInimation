"""
UAF-81.83: Client Network Engine with Prediction and Reconciliation.
"""

from __future__ import annotations

import copy
import json
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..models.definition import (
    AuthorityType,
    ChannelType,
    ConnectionState,
    DisconnectReason,
    EntitySnapshot,
    InputCommand,
    NetworkEntityId,
    NetworkMetrics,
    NetworkSnapshot,
    Packet,
    RPCMessage,
    RPCType,
    Vec3,
)
from ..prediction.client_predictor import ClientPredictor
from ..prediction.reconciliation import ReconciliationManager, ReconciliationResult
from ..protocol.channel import ReliableOrderedChannel, UnreliableSequencedChannel
from ..protocol.rpc import RPCDispatcher
from ..replication.delta import DeltaCompressor, DeltaSnapshot


class ClientNetworkEngine:
    """
    Client-side multiplayer network engine managing packet delivery,
    replicated entity state, local movement prediction, and server reconciliation.
    """

    def __init__(
        self,
        client_id: str,
        session_id: str = "sess_dedicated_01",
        tick_rate: int = 60,
    ):
        self.client_id = client_id
        self.session_id = session_id
        self.tick_rate = tick_rate
        self.connection_id: str = f"conn_{client_id}"

        self.state: ConnectionState = ConnectionState.DISCONNECTED
        self.client_tick: int = 0
        self.last_server_tick: int = 0
        self.last_acked_input_seq: int = 0
        self.input_sequence: int = 0

        # Channels
        self.reliable_channel = ReliableOrderedChannel()
        self.unreliable_channel = UnreliableSequencedChannel()

        # Replicated world state from server
        self.entities: Dict[NetworkEntityId, Dict[str, Any]] = {}

        # Local predicted entity
        self.local_net_id: Optional[NetworkEntityId] = None
        self.predictor: Optional[ClientPredictor] = None

        # RPC & Metrics
        self.rpc_dispatcher = RPCDispatcher()
        self.metrics = NetworkMetrics()

        # Outgoing queue for next tick
        self._outgoing_packets: List[Packet] = []

    def connect(self, connection_id: Optional[str] = None) -> None:
        """Initialize connection to server."""
        if connection_id:
            self.connection_id = connection_id
        self.state = ConnectionState.ACTIVE

    def setup_local_player(
        self,
        net_id: NetworkEntityId,
        initial_props: Dict[str, Any],
        simulation_fn: Optional[Callable[[Dict[str, Any], InputCommand, float], Dict[str, Any]]] = None,
    ) -> None:
        """Designate and initialize the locally predicted entity."""
        self.local_net_id = net_id
        self.entities[net_id] = copy.deepcopy(initial_props)
        self.predictor = ClientPredictor(
            net_id=net_id,
            initial_props=initial_props,
            simulation_fn=simulation_fn,
        )

    def queue_input(
        self,
        axes: Tuple[float, ...] = (0.0, 0.0),
        buttons: int = 0,
        actions: Tuple[str, ...] = (),
        dt: float = 1.0 / 60.0,
    ) -> InputCommand:
        """
        Produce a local input command, apply immediate prediction, and queue transmission.
        """
        self.input_sequence += 1
        cmd = InputCommand(
            client_tick=self.client_tick,
            sequence=self.input_sequence,
            buttons=buttons,
            axes=axes,
            actions=actions,
        )

        # Immediate local prediction
        if self.predictor:
            predicted = self.predictor.predict_input(cmd, dt=dt)
            if self.local_net_id:
                self.entities[self.local_net_id] = predicted
            self.metrics.prediction_ticks += 1

        # Package input for server transmission
        payload_data = {
            "type": "input",
            "command": {
                "client_tick": cmd.client_tick,
                "sequence": cmd.sequence,
                "buttons": cmd.buttons,
                "axes": list(cmd.axes),
                "actions": list(cmd.actions),
            },
        }
        payload_bytes = json.dumps(payload_data, separators=(",", ":")).encode("utf-8")

        pkt = self.unreliable_channel.prepare_send(
            session_id=self.session_id,
            connection_id=self.connection_id,
            server_tick=self.last_server_tick,
            payload=payload_bytes,
        )
        self._outgoing_packets.append(pkt)
        return cmd

    def receive_packet(self, packet: Packet) -> None:
        """Process incoming packet from server."""
        self.metrics.packets_received += 1
        self.metrics.bytes_received += len(packet.payload)

        delivered: List[Packet] = []
        if packet.header.channel == ChannelType.RELIABLE_ORDERED:
            delivered = self.reliable_channel.receive_packet(packet)
        else:
            p = self.unreliable_channel.receive_packet(packet)
            if p:
                delivered = [p]
            else:
                self.metrics.unreliable_dropped += 1

        for pkt in delivered:
            self._handle_delivered_packet(pkt)

    def _handle_delivered_packet(self, packet: Packet) -> None:
        """Parse server payload and update state."""
        try:
            raw_str = packet.payload.decode("utf-8")
            msg = json.loads(raw_str)
        except Exception:
            return

        msg_type = msg.get("type")

        # Delta snapshot received
        if msg_type == "delta_snapshot":
            server_tick = msg.get("server_tick", 0)
            if server_tick > self.last_server_tick:
                self.last_server_tick = server_tick

            delta_dict = msg.get("delta", {})
            delta = DeltaSnapshot.from_dict(delta_dict)

            # Apply delta to client world
            self.entities = DeltaCompressor.apply_delta(self.entities, delta)

            # Reconcile locally predicted entity if modified by server
            if self.local_net_id and self.predictor and self.local_net_id in self.entities:
                server_local_state = self.entities[self.local_net_id]
                res = self.predictor.reconcile_with_server(
                    server_state=server_local_state,
                    acked_sequence=self.last_acked_input_seq,
                )
                if res.reconciled:
                    self.metrics.reconciliation_count += 1
                    self.entities[self.local_net_id] = res.final_properties

            # Queue snapshot ACK to inform server of confirmed baseline
            ack_data = {
                "type": "snapshot_ack",
                "acked_tick": server_tick,
            }
            ack_bytes = json.dumps(ack_data, separators=(",", ":")).encode("utf-8")
            ack_pkt = self.unreliable_channel.prepare_send(
                session_id=self.session_id,
                connection_id=self.connection_id,
                server_tick=self.last_server_tick,
                payload=ack_bytes,
            )
            self._outgoing_packets.append(ack_pkt)

    def tick(self, dt: float = 1.0 / 60.0) -> List[Packet]:
        """Advance client tick and return pending packets for transport."""
        self.client_tick += 1
        pkts = list(self._outgoing_packets)
        self._outgoing_packets.clear()
        for p in pkts:
            self.metrics.packets_sent += 1
            self.metrics.bytes_sent += len(p.payload)
        return pkts

    def get_entity_property(self, net_id: NetworkEntityId, prop_name: str, default: Any = None) -> Any:
        """Get property from client-side replicated world state."""
        return self.entities.get(net_id, {}).get(prop_name, default)

    def get_local_predicted_position(self) -> Optional[Vec3]:
        """Return current predicted position of locally controlled entity."""
        if not self.local_net_id or self.local_net_id not in self.entities:
            return None
        pos = self.entities[self.local_net_id].get("position")
        if isinstance(pos, (list, tuple)) and len(pos) == 3:
            return (float(pos[0]), float(pos[1]), float(pos[2]))
        return None
