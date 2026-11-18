"""
UAF-81.83: Authoritative Dedicated Server Engine.
"""

from __future__ import annotations

import copy
import json
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..models.definition import (
    AuthorityType,
    ChannelType,
    ConnectionState,
    DisconnectReason,
    EntitySnapshot,
    InputCommand,
    NetworkEntityId,
    NetworkMetrics,
    NetworkSession,
    NetworkSnapshot,
    Packet,
    PacketValidationError,
    ReplicationPolicy,
    RPCMessage,
    RPCType,
    Vec3,
)
from ..prediction.history_buffer import HistoryBuffer
from ..prediction.input_buffer import InputBuffer
from ..prediction.lag_compensation import LagCompensator
from ..protocol.channel import ReliableOrderedChannel, UnreliableSequencedChannel
from ..protocol.rpc import RPCDispatcher
from ..replication.bandwidth import BandwidthArbiter
from ..replication.delta import DeltaCompressor, DeltaSnapshot
from ..replication.dormancy import DormancyManager
from ..replication.relevancy import SpatialRelevancyManager
from .connection import NetworkConnection


class DedicatedServerEngine:
    """
    Authoritative multiplayer server managing client connections, entity ownership,
    spatial relevancy, delta compression replication, lag compensation, and RPC dispatch.
    """

    def __init__(
        self,
        session_id: str = "sess_dedicated_01",
        tick_rate: int = 60,
    ):
        self.session = NetworkSession(session_id=session_id, tick_rate=tick_rate)
        self.server_tick: int = 0
        self.world_revision: int = 1

        # Connections: connection_id -> NetworkConnection
        self.connections: Dict[str, NetworkConnection] = {}
        self.client_to_conn: Dict[str, str] = {}

        # Authoritative Entities
        self.entities: Dict[NetworkEntityId, Dict[str, Any]] = {}
        self.entity_owners: Dict[NetworkEntityId, Optional[str]] = {}
        self.entity_revisions: Dict[NetworkEntityId, int] = {}

        # Client input queues: client_id -> InputBuffer
        self.client_inputs: Dict[str, InputBuffer] = {}

        # Subsystems
        self.relevancy_manager = SpatialRelevancyManager()
        self.dormancy_manager = DormancyManager()
        self.bandwidth_arbiter = BandwidthArbiter()
        self.history_buffer = HistoryBuffer(max_history_ticks=180)
        self.lag_compensator = LagCompensator(self.history_buffer, max_rewind_ticks=60)
        self.rpc_dispatcher = RPCDispatcher()
        self.metrics = NetworkMetrics()

        # Input processing hook: (client_id, input_cmd) -> None
        self.on_client_input: Optional[Callable[[str, InputCommand], None]] = None

    # --------------------------------------------------------------------------
    # Connection Management
    # --------------------------------------------------------------------------

    def register_connection(self, connection_id: str, client_id: str) -> NetworkConnection:
        """Accept a new client connection."""
        conn = NetworkConnection(connection_id=connection_id, client_id=client_id)
        conn.transition_to(ConnectionState.CONNECTING)
        conn.transition_to(ConnectionState.AUTHENTICATING)
        conn.transition_to(ConnectionState.CONNECTED)
        conn.transition_to(ConnectionState.ACTIVE)

        self.connections[connection_id] = conn
        self.client_to_conn[client_id] = connection_id
        self.client_inputs[client_id] = InputBuffer()
        self.metrics.connected_clients = len(self.connections)
        return conn

    def remove_connection(self, connection_id: str, reason: DisconnectReason = DisconnectReason.CLIENT_REQUEST) -> None:
        """Disconnect and clean up client connection."""
        conn = self.connections.pop(connection_id, None)
        if conn:
            conn.disconnect(reason)
            self.client_to_conn.pop(conn.client_id, None)
            self.client_inputs.pop(conn.client_id, None)
            self.relevancy_manager.remove_client(conn.client_id)
        self.metrics.connected_clients = len(self.connections)

    # --------------------------------------------------------------------------
    # Entity Management
    # --------------------------------------------------------------------------

    def spawn_entity(
        self,
        net_id: NetworkEntityId,
        initial_props: Dict[str, Any],
        owner_id: Optional[str] = None,
        policy: ReplicationPolicy = ReplicationPolicy.RELEVANT,
    ) -> None:
        """Spawn authoritative entity in the server world."""
        self.entities[net_id] = copy.deepcopy(initial_props)
        self.entity_owners[net_id] = owner_id
        self.entity_revisions[net_id] = 1

        pos = initial_props.get("position", (0.0, 0.0, 0.0))
        self.relevancy_manager.register_entity(
            net_id=net_id,
            policy=policy,
            owner_id=owner_id,
            position=tuple(pos) if isinstance(pos, (list, tuple)) else (0.0, 0.0, 0.0),
        )
        self.dormancy_manager.register_entity(net_id, current_tick=self.server_tick)
        self.bandwidth_arbiter.register_entity(net_id)
        self.world_revision += 1

    def destroy_entity(self, net_id: NetworkEntityId) -> None:
        """Destroy an authoritative entity."""
        self.entities.pop(net_id, None)
        self.entity_owners.pop(net_id, None)
        self.entity_revisions.pop(net_id, None)
        self.relevancy_manager.unregister_entity(net_id)
        self.dormancy_manager.unregister_entity(net_id)
        self.bandwidth_arbiter.unregister_entity(net_id)
        self.world_revision += 1

    def set_entity_property(self, net_id: NetworkEntityId, prop_name: str, value: Any) -> None:
        """Mutate an authoritative entity property."""
        if net_id in self.entities:
            self.entities[net_id][prop_name] = value
            self.entity_revisions[net_id] = self.entity_revisions.get(net_id, 0) + 1
            self.dormancy_manager.touch(net_id, self.server_tick)
            if prop_name == "position" and isinstance(value, (list, tuple)):
                self.relevancy_manager.update_entity_position(net_id, tuple(value))
            self.world_revision += 1

    def get_entity_property(self, net_id: NetworkEntityId, prop_name: str, default: Any = None) -> Any:
        """Retrieve entity property from authoritative state."""
        return self.entities.get(net_id, {}).get(prop_name, default)

    # --------------------------------------------------------------------------
    # Packet & RPC Processing
    # --------------------------------------------------------------------------

    def receive_packet(self, packet: Packet) -> None:
        """Process incoming packet from a client connection."""
        conn_id = packet.header.connection_id
        conn = self.connections.get(conn_id)
        if not conn:
            return

        conn.packets_received += 1
        conn.bytes_received += len(packet.payload)
        conn.last_activity_tick = self.server_tick
        self.metrics.packets_received += 1
        self.metrics.bytes_received += len(packet.payload)

        # Route through appropriate channel
        delivered_packets: List[Packet] = []
        if packet.header.channel == ChannelType.RELIABLE_ORDERED:
            delivered_packets = conn.reliable_channel.receive_packet(packet)
            self.metrics.reliable_sent += len(delivered_packets)
        else:
            p = conn.unreliable_channel.receive_packet(packet)
            if p is not None:
                delivered_packets = [p]
            else:
                self.metrics.unreliable_dropped += 1

        for pkt in delivered_packets:
            self._handle_delivered_payload(conn, pkt)

    def _handle_delivered_payload(self, conn: NetworkConnection, packet: Packet) -> None:
        """Decode and execute message contents."""
        try:
            raw_str = packet.payload.decode("utf-8")
            msg = json.loads(raw_str)
        except Exception:
            return

        msg_type = msg.get("type")

        # Snapshot ACK from client
        if msg_type == "snapshot_ack":
            acked_tick = msg.get("acked_tick", 0)
            conn.baseline_tracker.acknowledge_tick(acked_tick)

        # Input commands from client
        elif msg_type == "input":
            cmd_data = msg.get("command", {})
            cmd = InputCommand(
                client_tick=cmd_data.get("client_tick", 0),
                sequence=cmd_data.get("sequence", 0),
                buttons=cmd_data.get("buttons", 0),
                axes=tuple(cmd_data.get("axes", (0.0, 0.0))),
                actions=tuple(cmd_data.get("actions", ())),
            )
            input_buf = self.client_inputs.get(conn.client_id)
            if input_buf:
                input_buf.add_command(cmd)

        # RPC invocation
        elif msg_type == "rpc":
            rpc_data = msg.get("rpc", {})
            rpc_msg = RPCMessage(
                operation_id=rpc_data["op_id"],
                target_net_id=NetworkEntityId(namespace=rpc_data["ns"], value=rpc_data["val"]),
                rpc_name=rpc_data["name"],
                rpc_type=RPCType(rpc_data["type"]),
                payload=rpc_data.get("payload", {}),
            )
            # Check authority: client cannot invoke SERVER_AUTHORITY RPCs
            caller_auth = AuthorityType.CLIENT_PREDICTED
            self.rpc_dispatcher.dispatch(rpc_msg, caller_authority=caller_auth, context=conn)

    # --------------------------------------------------------------------------
    # Replication & Tick Execution
    # --------------------------------------------------------------------------

    def tick(self, dt: float = 1.0 / 60.0) -> Dict[str, List[Packet]]:
        """
        Advance one server logical tick:
        1. Process pending client inputs
        2. Update dormancy
        3. Record historical state in ring buffer
        4. Generate delta replication snapshots for connected clients
        """
        self.server_tick += 1

        # 1. Process client inputs
        for client_id, input_buf in self.client_inputs.items():
            input_buf.reset_tick_counter()
            while len(input_buf) > 0:
                cmd = input_buf.pop_oldest()
                if cmd and self.on_client_input:
                    self.on_client_input(client_id, cmd)

        # 2. Update dormancy
        self.dormancy_manager.update_auto_dormancy(self.server_tick)

        # 3. Record history snapshot
        self.history_buffer.record_state(self.server_tick, self.entities)

        # 4. Generate outgoing replication packets
        outgoing_packets = self.generate_replication_packets()
        return outgoing_packets

    def generate_replication_packets(self) -> Dict[str, List[Packet]]:
        """
        Build delta-compressed replication packets tailored for each active connection.
        """
        out: Dict[str, List[Packet]] = {}

        for conn_id, conn in self.connections.items():
            if not conn.is_active():
                continue

            # Identify relevant entities for this client
            relevant_ids = self.relevancy_manager.get_relevant_entities(conn.client_id)
            baseline_state = conn.baseline_tracker.get_confirmed_state()

            # Filter candidates using bandwidth arbiter
            candidate_ids = {nid for nid in relevant_ids if not self.dormancy_manager.is_dormant(nid)}
            scheduled_ids = set(self.bandwidth_arbiter.prioritize_entities(candidate_ids, self.server_tick))

            # Compute delta
            delta = DeltaCompressor.compute_delta(
                base_tick=conn.baseline_tracker.confirmed_tick,
                target_tick=self.server_tick,
                baseline_state=baseline_state,
                current_state=self.entities,
                entity_owners=self.entity_owners,
                relevant_entity_ids=scheduled_ids,
            )

            # Record outgoing snapshot in baseline history
            conn.baseline_tracker.record_snapshot(self.server_tick, self.entities)

            # Mark sent in bandwidth arbiter
            for d in delta.entity_deltas:
                self.bandwidth_arbiter.mark_sent(d.net_id, self.server_tick)

            # Package delta into payload
            payload_data = {
                "type": "delta_snapshot",
                "delta": delta.to_dict(),
                "server_tick": self.server_tick,
                "world_rev": self.world_revision,
            }
            payload_bytes = json.dumps(payload_data, separators=(",", ":")).encode("utf-8")

            # Prepare unreliable sequenced packet
            packet = conn.unreliable_channel.prepare_send(
                session_id=self.session.session_id,
                connection_id=conn.connection_id,
                server_tick=self.server_tick,
                payload=payload_bytes,
            )

            conn.packets_sent += 1
            conn.bytes_sent += len(packet.payload)
            self.metrics.packets_sent += 1
            self.metrics.bytes_sent += len(packet.payload)
            self.metrics.snapshots_sent += 1

            # Check for any reliable retransmissions
            retransmits = conn.reliable_channel.collect_retransmissions(self.server_tick)
            for ret in retransmits:
                self.metrics.reliable_retransmits += 1

            conn_packets = [packet] + retransmits
            out[conn_id] = conn_packets

        return out

    def get_canonical_snapshot(self) -> NetworkSnapshot:
        """Create a deterministic canonical state snapshot with SHA-256 hash."""
        snapshots = []
        for net_id, props in self.entities.items():
            snapshots.append(
                EntitySnapshot(
                    net_id=net_id,
                    owner_id=self.entity_owners.get(net_id),
                    properties=props,
                    revision=self.entity_revisions.get(net_id, 0),
                )
            )

        return NetworkSnapshot.create(
            server_tick=self.server_tick,
            world_revision=self.world_revision,
            active_connections=list(self.connections.keys()),
            entities=snapshots,
        )
