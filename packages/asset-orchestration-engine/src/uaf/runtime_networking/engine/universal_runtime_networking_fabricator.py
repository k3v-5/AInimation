"""
UAF-81.83: Universal Runtime Networking Fabricator and Deterministic Transport Simulator.
"""

from __future__ import annotations

import collections
import copy
import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

from ..models.definition import (
    AuthorityType,
    ChannelType,
    DisconnectReason,
    EntitySnapshot,
    InputCommand,
    NetworkEntityId,
    NetworkMetrics,
    NetworkSession,
    NetworkSnapshot,
    Packet,
    ReplicationPolicy,
    RPCMessage,
    RPCType,
    Vec3,
)
from .client import ClientNetworkEngine
from .connection import NetworkConnection
from .server import DedicatedServerEngine


@dataclass
class SimulatedTransportRule:
    """Configures deterministic network conditions for simulated transport."""
    packet_loss_rate: float = 0.0      # 0.0 to 1.0 (e.g. 0.05 for 5% loss)
    duplication_rate: float = 0.0      # 0.0 to 1.0 (e.g. 0.02 for 2% duplication)
    latency_ticks: int = 1             # Simulated one-way latency in ticks
    reorder_rate: float = 0.0          # 0.0 to 1.0 probability of packet reordering


class SimulatedNetworkTransport:
    """
    In-memory deterministic packet transport pipeline.
    Simulates latency, loss, duplicate packets, and reordering without opening OS sockets.
    """

    def __init__(self, rng_seed: int = 42, rule: Optional[SimulatedTransportRule] = None):
        self.rng = random.Random(rng_seed)
        self.rule = rule or SimulatedTransportRule()
        # In-flight queue: list of (deliver_at_tick, sender_id, recipient_id, packet)
        self._in_flight: List[Tuple[int, str, str, Packet]] = []

    def transmit(self, sender_id: str, recipient_id: str, packet: Packet, current_tick: int) -> None:
        """Enqueue packet for transmission according to simulated transport rules."""
        # 1. Packet Loss Check
        if self.rule.packet_loss_rate > 0.0 and self.rng.random() < self.rule.packet_loss_rate:
            return  # Dropped

        # 2. Compute delivery tick with simulated latency
        latency = self.rule.latency_ticks
        if self.rule.reorder_rate > 0.0 and self.rng.random() < self.rule.reorder_rate:
            latency += self.rng.randint(1, 3)

        deliver_tick = current_tick + latency
        self._in_flight.append((deliver_tick, sender_id, recipient_id, packet))

        # 3. Packet Duplication Check
        if self.rule.duplication_rate > 0.0 and self.rng.random() < self.rule.duplication_rate:
            self._in_flight.append((deliver_tick + 1, sender_id, recipient_id, copy.deepcopy(packet)))

    def deliver(self, current_tick: int) -> List[Tuple[str, str, Packet]]:
        """Deliver all packets scheduled for this tick or earlier."""
        delivered: List[Tuple[str, str, Packet]] = []
        remaining: List[Tuple[int, str, str, Packet]] = []

        for item in self._in_flight:
            deliver_tick, sender_id, recipient_id, pkt = item
            if current_tick >= deliver_tick:
                delivered.append((sender_id, recipient_id, pkt))
            else:
                remaining.append(item)

        self._in_flight = remaining
        return delivered

    def clear(self) -> None:
        self._in_flight.clear()


class UniversalRuntimeNetworkingFabricator:
    """
    Central orchestrator for headless multiplayer networking, client-server simulation,
    transport conditions, checkpoints, replay logging, and deterministic verification.
    """

    def __init__(
        self,
        session_id: str = "sess_uaf_golden_01",
        tick_rate: int = 60,
        rng_seed: int = 42,
        transport_rule: Optional[SimulatedTransportRule] = None,
    ):
        self.session_id = session_id
        self.tick_rate = tick_rate
        self.current_tick: int = 0

        # Dedicated Server Engine
        self.server = DedicatedServerEngine(session_id=session_id, tick_rate=tick_rate)

        # Connected Clients: client_id -> ClientNetworkEngine
        self.clients: Dict[str, ClientNetworkEngine] = {}

        # Simulated Transport Pipeline
        self.transport = SimulatedNetworkTransport(rng_seed=rng_seed, rule=transport_rule)

        # Checkpoints & Replay Log
        self.replays: List[Dict[str, Any]] = []

    def connect_client(self, client_id: str) -> ClientNetworkEngine:
        """Register client with server and initialize client networking engine."""
        conn_id = f"conn_{client_id}"
        self.server.register_connection(conn_id, client_id)

        client = ClientNetworkEngine(client_id=client_id, session_id=self.session_id, tick_rate=self.tick_rate)
        client.connect(conn_id)
        self.clients[client_id] = client
        return client

    def disconnect_client(self, client_id: str, reason: DisconnectReason = DisconnectReason.CLIENT_REQUEST) -> None:
        """Disconnect client from server."""
        client = self.clients.pop(client_id, None)
        if client:
            client.state = ConnectionState.DISCONNECTED
        conn_id = f"conn_{client_id}"
        self.server.remove_connection(conn_id, reason)

    def step(self, dt: float = 1.0 / 60.0) -> None:
        """
        Execute one complete distributed simulation step across clients and server:
        1. Clients tick & enqueue inputs to transport.
        2. Deliver client -> server packets.
        3. Server ticks (processes inputs, records history, emits delta packets).
        4. Deliver server -> client packets.
        5. Clients receive snapshots & perform reconciliation.
        """
        self.current_tick += 1

        # 1. Clients tick
        for client_id, client in self.clients.items():
            outgoing = client.tick(dt=dt)
            for pkt in outgoing:
                self.transport.transmit(client_id, "server", pkt, self.current_tick)

        # 2. Deliver client -> server
        incoming_to_server = self.transport.deliver(self.current_tick)
        for sender_id, recipient_id, pkt in incoming_to_server:
            if recipient_id == "server":
                self.server.receive_packet(pkt)

        # 3. Server tick
        server_outgoing = self.server.tick(dt=dt)
        for conn_id, pkts in server_outgoing.items():
            conn = self.server.connections.get(conn_id)
            if conn:
                for pkt in pkts:
                    self.transport.transmit("server", conn.client_id, pkt, self.current_tick)

        # 4. Deliver server -> client
        incoming_to_clients = self.transport.deliver(self.current_tick)
        for sender_id, recipient_id, pkt in incoming_to_clients:
            client = self.clients.get(recipient_id)
            if client:
                client.receive_packet(pkt)

    def create_checkpoint(self) -> Dict[str, Any]:
        """Generate deterministic serializable checkpoint of entire distributed session."""
        snapshot = self.server.get_canonical_snapshot()
        entities_data = []
        for net_id, props in self.server.entities.items():
            entities_data.append({
                "ns": net_id.namespace,
                "val": net_id.value,
                "owner": self.server.entity_owners.get(net_id),
                "rev": self.server.entity_revisions.get(net_id, 0),
                "props": copy.deepcopy(props),
            })

        return {
            "session_id": self.session_id,
            "server_tick": self.server.server_tick,
            "world_revision": self.server.world_revision,
            "state_hash": snapshot.state_hash,
            "connections": list(self.server.connections.keys()),
            "entities": entities_data,
        }

    def restore_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Restore server authoritative state from checkpoint."""
        self.server.server_tick = checkpoint["server_tick"]
        self.server.world_revision = checkpoint["world_revision"]
        self.server.entities.clear()
        self.server.entity_owners.clear()
        self.server.entity_revisions.clear()

        for e in checkpoint.get("entities", []):
            net_id = NetworkEntityId(namespace=e["ns"], value=e["val"])
            self.server.entities[net_id] = copy.deepcopy(e["props"])
            self.server.entity_owners[net_id] = e["owner"]
            self.server.entity_revisions[net_id] = e.get("rev", 0)

        self.transport.clear()

    def get_state_hash(self) -> str:
        """Return canonical SHA-256 state hash of server state."""
        return self.server.get_canonical_snapshot().state_hash
