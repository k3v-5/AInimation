"""
Acceptance Test Suite for UAF-81.83:
Universal Runtime Networking, Entity Replication, State Synchronization & Multiplayer Engine.

Validates:
1. Stable Identities, Snapshot Hashing & Numeric Security.
2. Modular Sequence Number Arithmetic & 32-bit Sliding ACK Window.
3. Binary Packet Serialization & CRC32 Integrity Checking.
4. Reliable Ordered & Unreliable Sequenced Network Channels.
5. RPC Dispatcher, Authority Enforcement & Idempotency Cache.
6. Property Quantization, Dirty Tracking & Delta Compression.
7. Spatial Relevancy, Dormancy & Bandwidth Scheduling.
8. Client Prediction, Desync Detection & Reconciliation Replay.
9. Lag Compensation (Rewind Hit Validation) & Server-side Rollback Resimulation.
10. Connection State Machine Transitions.
11. Semantic Validator & UE5 Packaging Manifest.
12. Golden Multiplayer Scenario (Dedicated Server + 4 Clients + 100 AI + 1000 Replicated Entities under loss/duplication/jitter).
"""

import copy
import math
from typing import Dict, List, Tuple
import pytest

from uaf.runtime_networking import (
    AckManager,
    AuthorityType,
    BandwidthArbiter,
    BandwidthBudget,
    BaselineInvalidatedError,
    ChannelType,
    ClientBaselineTracker,
    ClientId,
    ClientNetworkEngine,
    ClientPredictor,
    ConnectionId,
    ConnectionState,
    ConnectionStateError,
    DedicatedServerEngine,
    DeltaCompressor,
    DeltaSnapshot,
    DesyncError,
    DisconnectReason,
    DormancyManager,
    DormancyState,
    EntityDelta,
    EntitySnapshot,
    HistoryBuffer,
    InputCommand,
    InputBuffer,
    InterestProfile,
    InvalidAuthorityError,
    LagCompensator,
    NetworkConnection,
    NetworkEntityId,
    NetworkError,
    NetworkMetrics,
    NetworkMode,
    NetworkPriority,
    NetworkSession,
    NetworkSnapshot,
    NetworkValidationIssue,
    NumericSecurityError,
    OwnershipType,
    Packet,
    PacketHeader,
    PacketSerializer,
    PacketValidationError,
    PropertyContainer,
    RateLimitExceededError,
    ReconciliationManager,
    ReconciliationResult,
    ReliableOrderedChannel,
    ReplicationPolicy,
    RollbackEngine,
    RollbackError,
    RPCDispatcher,
    RPCMessage,
    RPCType,
    SimulatedNetworkTransport,
    SimulatedTransportRule,
    SpatialRelevancyManager,
    UnreliableSequencedChannel,
    UniversalRuntimeNetworkingFabricator,
    UniversalRuntimeNetworkingPackager,
    UniversalRuntimeNetworkingValidator,
    ensure_finite_float,
    ensure_finite_vec3,
    quantize_value,
    sequence_diff,
    sequence_greater_than,
    sequence_less_than,
)


# ==============================================================================
# 1. IDENTITIES, SNAPSHOT HASHING & NUMERIC SECURITY
# ==============================================================================

def test_network_entity_id_ordering_and_hashing():
    id1 = NetworkEntityId(namespace=1, value=10)
    id2 = NetworkEntityId(namespace=1, value=20)
    id3 = NetworkEntityId(namespace=2, value=5)

    assert id1 < id2
    assert id2 < id3
    assert str(id1) == "NetId(1:10)"

    s = {id1, id2, id3}
    assert id1 in s
    assert len(s) == 3


def test_numeric_security_nan_and_infinity_rejected():
    with pytest.raises(NumericSecurityError):
        ensure_finite_float(float("nan"), "test")

    with pytest.raises(NumericSecurityError):
        ensure_finite_float(float("inf"), "test")

    with pytest.raises(NumericSecurityError):
        ensure_finite_vec3((1.0, float("nan"), 0.0), "test_vec")

    with pytest.raises(NumericSecurityError):
        InputCommand(client_tick=1, sequence=1, axes=(0.0, float("inf")))

    # Valid values should pass
    val = ensure_finite_float(42.5, "valid")
    assert val == 42.5
    vec = ensure_finite_vec3((1.0, 2.0, 3.0), "valid_vec")
    assert vec == (1.0, 2.0, 3.0)


def test_network_snapshot_canonical_sha256_determinism():
    e1 = EntitySnapshot(net_id=NetworkEntityId(1, 1), owner_id="c1", properties={"x": 10, "name": "hero"})
    e2 = EntitySnapshot(net_id=NetworkEntityId(1, 2), owner_id="c2", properties={"health": 100})

    snap_a = NetworkSnapshot.create(10, 1, ["conn_1", "conn_2"], [e2, e1])
    snap_b = NetworkSnapshot.create(10, 1, ["conn_2", "conn_1"], [e1, e2])

    assert snap_a.state_hash == snap_b.state_hash
    assert len(snap_a.state_hash) == 64  # SHA-256 hex digest
    assert snap_a.entity_count == 2


# ==============================================================================
# 2. SEQUENCE NUMBERS & SLIDING ACK WINDOW
# ==============================================================================

def test_modular_sequence_arithmetic_and_wrapping():
    # Normal sequential comparison
    assert sequence_greater_than(10, 5)
    assert sequence_less_than(5, 10)
    assert sequence_diff(10, 5) == 5

    # 16-bit integer wrapping (around 65536)
    # 2 is newer than 65534 across the wrap boundary
    assert sequence_greater_than(2, 65534)
    assert sequence_less_than(65534, 2)
    assert sequence_diff(2, 65534) == 4

    # 65530 is older than 5
    assert sequence_greater_than(5, 65530)
    assert sequence_diff(5, 65530) == 11


def test_sliding_ack_window():
    mgr = AckManager()

    # Receive sequence 10
    mgr.register_received_sequence(10)
    ack, ack_bits = mgr.get_ack_info()
    assert ack == 10
    assert ack_bits == 0

    # Receive sequence 9 and 8 (in-order or out-of-order)
    mgr.register_received_sequence(9)
    mgr.register_received_sequence(8)
    ack, ack_bits = mgr.get_ack_info()
    assert ack == 10
    # Bit 0 (offset 1, seq 9) and Bit 1 (offset 2, seq 8) should be set: 1 | 2 = 3
    assert (ack_bits & 0b11) == 0b11

    # Verify acknowledgement queries
    assert mgr.is_acknowledged(10, ack, ack_bits)
    assert mgr.is_acknowledged(9, ack, ack_bits)
    assert mgr.is_acknowledged(8, ack, ack_bits)
    assert not mgr.is_acknowledged(7, ack, ack_bits)
    assert not mgr.is_acknowledged(11, ack, ack_bits)


# ==============================================================================
# 3. PACKET SERIALIZATION & CRC32
# ==============================================================================

def test_packet_serialization_roundtrip_and_crc_corruption():
    header = PacketHeader(
        protocol_version=1,
        session_id="sess_test",
        connection_id="conn_01",
        channel=ChannelType.RELIABLE_ORDERED,
        sequence=42,
        ack=40,
        ack_bits=0b11,
        server_tick=120,
        payload_size=11,
    )
    payload = b"hello world"
    pkt = Packet(header=header, payload=payload)

    encoded = PacketSerializer.encode(pkt)
    assert len(encoded) > len(payload)

    # Decode valid packet
    decoded = PacketSerializer.decode(encoded, expected_protocol=1)
    assert decoded.header.sequence == 42
    assert decoded.header.channel == ChannelType.RELIABLE_ORDERED
    assert decoded.payload == b"hello world"
    assert decoded.header.session_id == "sess_test"

    # Corrupt a payload byte to trigger CRC32 failure
    corrupted = bytearray(encoded)
    corrupted[-1] = (corrupted[-1] + 1) % 256
    with pytest.raises(PacketValidationError, match="checksum mismatch"):
        PacketSerializer.decode(bytes(corrupted), expected_protocol=1)

    # Protocol version mismatch
    with pytest.raises(PacketValidationError, match="Protocol version mismatch"):
        PacketSerializer.decode(encoded, expected_protocol=2)


# ==============================================================================
# 4. CHANNELS: RELIABLE ORDERED & UNRELIABLE SEQUENCED
# ==============================================================================

def test_reliable_ordered_channel_delivers_in_order_with_retransmits():
    sender = ReliableOrderedChannel(rto_ticks=3)
    receiver = ReliableOrderedChannel(rto_ticks=3)

    # Prepare packets 1, 2, 3
    p1 = sender.prepare_send("s1", "c1", 10, b"p1", current_tick=1)
    p2 = sender.prepare_send("s1", "c1", 10, b"p2", current_tick=1)
    p3 = sender.prepare_send("s1", "c1", 10, b"p3", current_tick=1)

    # Simulate packet 1 dropped, packet 2 and 3 arrive out-of-order
    deliv_2 = receiver.receive_packet(p2)
    assert deliv_2 == []  # Cannot deliver p2 before p1

    deliv_3 = receiver.receive_packet(p3)
    assert deliv_3 == []  # Still waiting for p1

    # Sender detects timeout on tick 5 (1 + 3 = 4 < 5)
    retransmits = sender.collect_retransmissions(current_tick=5)
    assert any(p.payload == b"p1" for p in retransmits)

    # Deliver p1 to receiver -> should immediately deliver p1, p2, p3 contiguous
    deliv_all = receiver.receive_packet(p1)
    assert len(deliv_all) == 3
    assert [p.payload for p in deliv_all] == [b"p1", b"p2", b"p3"]

    # Duplicate p1 should be silently dropped
    dup = receiver.receive_packet(p1)
    assert dup == []


def test_unreliable_sequenced_channel_drops_old_packets():
    sender = UnreliableSequencedChannel()
    receiver = UnreliableSequencedChannel()

    p1 = sender.prepare_send("s1", "c1", 10, b"u1")
    p2 = sender.prepare_send("s1", "c1", 11, b"u2")
    p3 = sender.prepare_send("s1", "c1", 12, b"u3")

    # Deliver p2 first
    r2 = receiver.receive_packet(p2)
    assert r2 is not None
    assert r2.payload == b"u2"

    # Old packet p1 arrives late -> dropped!
    r1 = receiver.receive_packet(p1)
    assert r1 is None

    # Newer packet p3 arrives -> accepted!
    r3 = receiver.receive_packet(p3)
    assert r3 is not None
    assert r3.payload == b"u3"


# ==============================================================================
# 5. RPC DISPATCHER, AUTHORITY & IDEMPOTENCY
# ==============================================================================

def test_rpc_dispatcher_authority_and_idempotency():
    dispatcher = RPCDispatcher()
    executed_count = 0

    def on_server_deal_damage(msg: RPCMessage, ctx):
        nonlocal executed_count
        executed_count += 1
        return {"damage_applied": msg.payload.get("amount", 0)}

    dispatcher.register_handler(
        "DealDamage",
        on_server_deal_damage,
        required_authority=AuthorityType.SERVER_AUTHORITY,
    )

    rpc = RPCMessage(
        operation_id="op_dmg_001",
        target_net_id=NetworkEntityId(1, 10),
        rpc_name="DealDamage",
        rpc_type=RPCType.RELIABLE_SERVER,
        payload={"amount": 25},
    )

    # 1. Unprivileged client attempting to call SERVER_AUTHORITY RPC directly fails
    with pytest.raises(InvalidAuthorityError):
        dispatcher.dispatch(rpc, caller_authority=AuthorityType.CLIENT_PREDICTED)

    assert executed_count == 0

    # 2. Server authority executes successfully
    res1 = dispatcher.dispatch(rpc, caller_authority=AuthorityType.SERVER_AUTHORITY)
    assert res1 == {"damage_applied": 25}
    assert executed_count == 1

    # 3. Idempotency: duplicate RPC with same operation_id returns cached result without re-executing
    res2 = dispatcher.dispatch(rpc, caller_authority=AuthorityType.SERVER_AUTHORITY)
    assert res2 == {"damage_applied": 25}
    assert executed_count == 1  # Not executed again!


# ==============================================================================
# 6. PROPERTY QUANTIZATION, DIRTY TRACKING & DELTA COMPRESSION
# ==============================================================================

def test_property_container_quantization_and_dirty_flags():
    container = PropertyContainer()
    container.register_property("position", (10.1234, 20.5678, 30.9999), quantization="vec3_2")
    container.register_property("health", 100.0, quantization="int")

    assert container.get_property("position") == (10.12, 20.57, 31.0)
    assert container.get_property("health") == 100
    assert container.is_dirty()

    container.clear_dirty()
    assert not container.is_dirty()

    # Setting value within quantization tolerance shouldn't mark dirty
    changed = container.set_property("position", (10.121, 20.572, 31.001))
    assert not changed
    assert not container.is_dirty()

    # Setting distinct value marks dirty
    changed = container.set_property("position", (11.0, 20.0, 30.0))
    assert changed
    assert container.is_dirty()


def test_delta_compression_and_state_reconstruction():
    net1 = NetworkEntityId(1, 101)
    net2 = NetworkEntityId(1, 102)

    # Initial baseline confirmed state
    baseline_state = {
        net1: {"position": (0.0, 0.0, 0.0), "health": 100},
    }

    # Current world state: net1 moved, net2 spawned
    current_state = {
        net1: {"position": (5.0, 0.0, 0.0), "health": 100},
        net2: {"position": (10.0, 2.0, 0.0), "health": 50},
    }

    delta = DeltaCompressor.compute_delta(
        base_tick=10,
        target_tick=15,
        baseline_state=baseline_state,
        current_state=current_state,
    )

    assert delta.base_tick == 10
    assert delta.target_tick == 15
    assert len(delta.entity_deltas) == 2

    # Verify net1 only sends changed position, not health
    d1 = next(d for d in delta.entity_deltas if d.net_id == net1)
    assert not d1.is_spawn
    assert d1.changed_properties == {"position": (5.0, 0.0, 0.0)}

    # Verify net2 sends spawn
    d2 = next(d for d in delta.entity_deltas if d.net_id == net2)
    assert d2.is_spawn

    # Apply delta to baseline and verify exact match with current_state
    reconstructed = DeltaCompressor.apply_delta(baseline_state, delta)
    assert reconstructed == current_state


# ==============================================================================
# 7. SPATIAL RELEVANCY, DORMANCY & BANDWIDTH SCHEDULING
# ==============================================================================

def test_spatial_relevancy_and_interest_filtering():
    relevancy = SpatialRelevancyManager()
    e_near = NetworkEntityId(1, 1)
    e_far = NetworkEntityId(1, 2)
    e_always = NetworkEntityId(1, 3)

    relevancy.register_entity(e_near, policy=ReplicationPolicy.RELEVANT, position=(10.0, 0.0, 0.0))
    relevancy.register_entity(e_far, policy=ReplicationPolicy.RELEVANT, position=(500.0, 0.0, 0.0))
    relevancy.register_entity(e_always, policy=ReplicationPolicy.ALWAYS, position=(1000.0, 0.0, 0.0))

    # Client is at origin with 50m radius
    relevancy.set_client_interest("client_A", InterestProfile(position=(0.0, 0.0, 0.0), radius=50.0))

    relevant = relevancy.get_relevant_entities("client_A")
    assert e_near in relevant
    assert e_always in relevant
    assert e_far not in relevant  # Filtered out!


def test_dormancy_and_touch_reactivation():
    dormancy = DormancyManager(default_idle_ticks=10)
    nid = NetworkEntityId(1, 5)

    dormancy.register_entity(nid, initial_state=DormancyState.ACTIVE, current_tick=0)
    assert not dormancy.is_dormant(nid)

    # After 10 ticks without update, entity becomes dormant
    dormancy.update_auto_dormancy(current_tick=10)
    assert dormancy.is_dormant(nid)

    # Touch wakes it up
    dormancy.touch(nid, current_tick=11)
    assert not dormancy.is_dormant(nid)


def test_bandwidth_arbiter_starvation_prevention():
    arbiter = BandwidthArbiter()
    e_high = NetworkEntityId(1, 1)
    e_low = NetworkEntityId(1, 2)

    arbiter.register_entity(e_high, priority=NetworkPriority.HIGH)
    arbiter.register_entity(e_low, priority=NetworkPriority.LOW)

    # Initially high priority comes first
    ranked = arbiter.prioritize_entities({e_high, e_low}, current_tick=1)
    assert ranked == [e_high, e_low]

    # e_high is repeatedly marked sent, while e_low starves for 100 ticks
    arbiter.mark_sent(e_high, current_tick=1)
    arbiter.mark_sent(e_high, current_tick=50)

    # Now check at tick 100: e_low accumulated priority surpasses e_high!
    ranked_later = arbiter.prioritize_entities({e_high, e_low}, current_tick=100)
    assert ranked_later[0] == e_low


# ==============================================================================
# 8. PREDICTION, RECONCILIATION & ROLLBACK
# ==============================================================================

def test_client_prediction_and_reconciliation_replay():
    net_id = NetworkEntityId(1, 10)
    initial_props = {"position": (0.0, 0.0, 0.0), "speed": 10.0}
    predictor = ClientPredictor(net_id=net_id, initial_props=initial_props)

    # Apply 3 inputs locally: moves along X axis
    c1 = predictor.predict_input(InputCommand(client_tick=1, sequence=1, axes=(1.0, 0.0)))
    c2 = predictor.predict_input(InputCommand(client_tick=2, sequence=2, axes=(1.0, 0.0)))
    c3 = predictor.predict_input(InputCommand(client_tick=3, sequence=3, axes=(1.0, 0.0)))

    predicted_pos = predictor.current_state["position"]
    assert predicted_pos[0] > 0.0

    # Server sends authoritative state at sequence 1, confirming position (no divergence)
    server_props_ok = {"position": c1["position"], "speed": 10.0}
    res_ok = predictor.reconcile_with_server(server_props_ok, acked_sequence=1)
    assert not res_ok.reconciled
    assert len(predictor.unacked_inputs) == 2  # inputs 2 and 3 remain

    # Server sends authoritative state at sequence 2 with divergence (e.g. server obstacle collided and set X=0.0)
    server_props_diverged = {"position": (0.0, 0.0, 0.0), "speed": 10.0}
    res_div = predictor.reconcile_with_server(server_props_diverged, acked_sequence=2)

    assert res_div.reconciled
    assert res_div.replayed_ticks == 1  # Replayed input sequence 3
    # Resulting position is starting from (0,0,0) plus input 3
    assert res_div.final_properties["position"][0] < predicted_pos[0]


def test_lag_compensation_rewind_hit_validation():
    history = HistoryBuffer(max_history_ticks=60)
    lag_comp = LagCompensator(history_buffer=history, max_rewind_ticks=30)
    target_id = NetworkEntityId(1, 99)

    # Record past states: target moves from (0,0,0) at tick 10 to (50,0,0) at tick 20
    history.record_state(10, {target_id: {"position": (0.0, 0.0, 0.0)}})
    history.record_state(20, {target_id: {"position": (50.0, 0.0, 0.0)}})

    current_tick = 20
    target_tick = 10

    # Shot at impact point (0.5, 0.0, 0.0) matches historical tick 10 position (0,0,0)
    hit_valid = lag_comp.verify_proximity_hit(
        current_tick=current_tick,
        target_tick=target_tick,
        target_id=target_id,
        impact_point=(0.5, 0.0, 0.0),
        tolerance_radius=1.0,
    )
    assert hit_valid

    # Shot at (50, 0, 0) for historical tick 10 should fail (target wasn't there yet!)
    hit_invalid = lag_comp.verify_proximity_hit(
        current_tick=current_tick,
        target_tick=target_tick,
        target_id=target_id,
        impact_point=(50.0, 0.0, 0.0),
        tolerance_radius=1.0,
    )
    assert not hit_invalid

    # Attempt to rewind beyond max allowed depth fails
    assert not lag_comp.verify_proximity_hit(
        current_tick=100,
        target_tick=10,  # 90 ticks ago > max 30
        target_id=target_id,
        impact_point=(0.0, 0.0, 0.0),
    )


def test_rollback_engine_resimulation():
    history = HistoryBuffer(max_history_ticks=60)
    nid = NetworkEntityId(1, 1)

    # Define simple simulation: position.x += 1.0 per tick
    def sim_step(states, tick, dt):
        st = copy.deepcopy(states)
        if nid in st:
            pos = st[nid]["position"]
            st[nid]["position"] = (pos[0] + 1.0, pos[1], pos[2])
        return st

    rollback = RollbackEngine(history_buffer=history, simulation_step_fn=sim_step, max_rollback_ticks=30)

    # Populate ticks 10 to 15
    curr_state = {nid: {"position": (0.0, 0.0, 0.0)}}
    for t in range(10, 16):
        history.record_state(t, curr_state)
        curr_state = sim_step(curr_state, t, 1.0 / 60.0)

    # Rollback from tick 15 to tick 12 with a hook modifying state
    def late_input_hook(state, tick):
        pos = state[nid]["position"]
        state[nid]["position"] = (pos[0] + 10.0, pos[1], pos[2])

    resimulated_state = rollback.execute_rollback_resimulation(
        current_tick=15,
        target_tick=12,
        pre_step_hook=late_input_hook,
    )

    assert rollback.rollback_count == 1
    # Check that the resimulated state incorporated the late input
    assert resimulated_state[nid]["position"][0] > 10.0


# ==============================================================================
# 9. CONNECTION STATE MACHINE & SECURITY VALIDATION
# ==============================================================================

def test_connection_state_machine_legal_and_illegal_transitions():
    conn = NetworkConnection("c1", "client_1")
    assert conn.state == ConnectionState.DISCONNECTED

    # Legal progression
    conn.transition_to(ConnectionState.CONNECTING)
    conn.transition_to(ConnectionState.AUTHENTICATING)
    conn.transition_to(ConnectionState.CONNECTED)
    conn.transition_to(ConnectionState.ACTIVE)
    assert conn.is_active()

    # Illegal transition: cannot go directly from ACTIVE to AUTHENTICATING
    with pytest.raises(ConnectionStateError):
        conn.transition_to(ConnectionState.AUTHENTICATING)

    conn.disconnect(DisconnectReason.SERVER_SHUTDOWN)
    assert conn.state == ConnectionState.DISCONNECTED
    assert conn.disconnect_reason == DisconnectReason.SERVER_SHUTDOWN


def test_semantic_validator_catches_violations():
    server = DedicatedServerEngine(session_id="srv_val", tick_rate=60)
    net_bad = NetworkEntityId(1, 999)

    # Inject invalid NaN position
    server.entities[net_bad] = {"position": (float("nan"), 0.0, 0.0)}

    issues = UniversalRuntimeNetworkingValidator.validate_server(server)
    assert any(i.code == "NET_NUMERIC_ERROR" for i in issues)


def test_ue5_packaging_manifest_generation():
    fabricator = UniversalRuntimeNetworkingFabricator(session_id="sess_ue5_pack")
    fabricator.connect_client("client_01")
    fabricator.server.spawn_entity(NetworkEntityId(1, 10), {"position": (1.0, 2.0, 3.0), "name": "Spawner"})

    manifest = UniversalRuntimeNetworkingPackager.package_network_session(fabricator)
    assert manifest["SchemaVersion"] == "1.0.0"
    assert manifest["UAF_Networking_System"] == "81.83"
    assert "UE5_NetDriver" in manifest
    assert "UE5_ReplicationGraph" in manifest
    assert "ManifestHash" in manifest
    assert len(manifest["ManifestHash"]) == 64


# ==============================================================================
# 10. GOLDEN MULTIPLAYER SCENARIO
# ==============================================================================

def test_golden_multiplayer_scenario():
    """
    Simulates a complete multiplayer distributed world:
    - 1 Dedicated Server.
    - 4 Connected Clients.
    - 100 AI Agents moving dynamically on the server.
    - 1,000 Replicated Entities.
    - Simulated transport with 5% packet loss, 2% duplication, latency, and jitter.
    - Runs 30 distributed frames.
    - Verifies delta synchronization, prediction, reconciliation, and SHA-256 state checkpoint.
    """
    rule = SimulatedTransportRule(
        packet_loss_rate=0.05,
        duplication_rate=0.02,
        latency_ticks=2,
        reorder_rate=0.05,
    )

    fabricator = UniversalRuntimeNetworkingFabricator(
        session_id="sess_golden_multiplayer",
        tick_rate=60,
        rng_seed=1337,
        transport_rule=rule,
    )

    # 1. Connect 4 clients
    client_ids = [f"client_{i}" for i in range(1, 5)]
    clients = [fabricator.connect_client(cid) for cid in client_ids]
    assert len(fabricator.server.connections) == 4

    # 2. Setup local player entity for each client
    for i, c in enumerate(clients):
        player_net_id = NetworkEntityId(1, 1000 + i)
        start_pos = (float(i * 10), 0.0, 0.0)
        fabricator.server.spawn_entity(
            net_id=player_net_id,
            initial_props={"position": start_pos, "speed": 10.0, "role": "player"},
            owner_id=c.client_id,
            policy=ReplicationPolicy.ALWAYS,
        )
        c.setup_local_player(player_net_id, {"position": start_pos, "speed": 10.0, "role": "player"})

    # 3. Spawn 100 AI agents (namespace 2)
    for aid in range(100):
        ai_net_id = NetworkEntityId(2, aid)
        pos = (float(aid % 10 * 5), float(aid // 10 * 5), 0.0)
        fabricator.server.spawn_entity(
            net_id=ai_net_id,
            initial_props={"position": pos, "health": 100, "ai_state": "patrol"},
            policy=ReplicationPolicy.RELEVANT,
        )

    # 4. Spawn 1000 static/replicated environmental props (namespace 3)
    for pid in range(1000):
        prop_net_id = NetworkEntityId(3, pid)
        pos = (float(pid % 50 * 4), float(pid // 50 * 4), 0.0)
        fabricator.server.spawn_entity(
            net_id=prop_net_id,
            initial_props={"position": pos, "type": "foliage", "destructible": False},
            policy=ReplicationPolicy.RELEVANT,
        )

    assert len(fabricator.server.entities) == 1104

    # Hook server input processing to move players
    def server_input_handler(client_id: str, cmd: InputCommand):
        # Move client's owned player on server
        for net_id, owner in fabricator.server.entity_owners.items():
            if owner == client_id:
                pos = fabricator.server.get_entity_property(net_id, "position", (0.0, 0.0, 0.0))
                speed = 10.0
                dt = 1.0 / 60.0
                new_x = pos[0] + cmd.axes[0] * speed * dt
                new_y = pos[1] + cmd.axes[1] * speed * dt
                new_z = pos[2]
                fabricator.server.set_entity_property(
                    net_id, "position", (round(new_x, 4), round(new_y, 4), round(new_z, 4))
                )

    fabricator.server.on_client_input = server_input_handler

    # 5. Run 30 distributed ticks
    for tick in range(1, 31):
        # Clients produce input: client 1 moves right, client 2 moves up, etc.
        clients[0].queue_input(axes=(1.0, 0.0))
        clients[1].queue_input(axes=(0.0, 1.0))
        clients[2].queue_input(axes=(-1.0, 0.0))
        clients[3].queue_input(axes=(0.0, -1.0))

        # AI movement step on server
        for aid in range(10):  # move a subset of AIs each tick
            ai_id = NetworkEntityId(2, aid)
            pos = fabricator.server.get_entity_property(ai_id, "position", (0.0, 0.0, 0.0))
            fabricator.server.set_entity_property(ai_id, "position", (pos[0] + 0.1, pos[1], pos[2]))

        fabricator.step()

    # 6. Verify distributed session invariants
    assert fabricator.server.server_tick == 30
    assert fabricator.server.metrics.snapshots_sent > 0
    assert fabricator.server.metrics.packets_sent > 0

    # Check that client 1 predicted movement
    pos_client_1 = clients[0].get_local_predicted_position()
    assert pos_client_1 is not None
    assert pos_client_1[0] > 0.0  # moved along X

    # 7. Checkpoint creation and restoration verify exact SHA-256 state matching
    checkpoint = fabricator.create_checkpoint()
    state_hash_1 = checkpoint["state_hash"]
    assert len(state_hash_1) == 64

    # Mutate server state
    test_ent = NetworkEntityId(1, 1000)
    fabricator.server.set_entity_property(test_ent, "position", (999.0, 999.0, 999.0))
    mutated_hash = fabricator.get_state_hash()
    assert mutated_hash != state_hash_1

    # Restore checkpoint and verify restored hash matches state_hash_1
    fabricator.restore_checkpoint(checkpoint)
    restored_hash = fabricator.get_state_hash()
    assert restored_hash == state_hash_1
