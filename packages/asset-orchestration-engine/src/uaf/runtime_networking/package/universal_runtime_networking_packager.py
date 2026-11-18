"""
UAF-81.83: Packaging and Unreal Engine 5 Network Driver & Replication Graph Manifests.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from ..engine.universal_runtime_networking_fabricator import UniversalRuntimeNetworkingFabricator


class UniversalRuntimeNetworkingPackager:
    """Packages multiplayer state and replication graphs for interoperability with Unreal Engine 5."""

    @classmethod
    def package_network_session(cls, fabricator: UniversalRuntimeNetworkingFabricator) -> Dict[str, Any]:
        server = fabricator.server

        # Replicated actors/entities export
        replicated_actors = []
        for net_id in sorted(server.entities.keys(), key=lambda i: (i.namespace, i.value)):
            props = server.entities[net_id]
            owner = server.entity_owners.get(net_id)
            policy = server.relevancy_manager._entity_policies.get(net_id)

            replicated_actors.append({
                "NetworkEntityId": f"{net_id.namespace}:{net_id.value}",
                "OwnerId": owner or "",
                "ReplicationPolicy": policy.value if policy else "RELEVANT",
                "Revision": server.entity_revisions.get(net_id, 0),
                "Properties": {k: props[k] for k in sorted(props.keys())},
            })

        # Connected clients export
        clients_data = []
        for conn_id in sorted(server.connections.keys()):
            conn = server.connections[conn_id]
            clients_data.append({
                "ConnectionId": conn.connection_id,
                "ClientId": conn.client_id,
                "State": conn.state.value,
                "ConfirmedBaselineTick": conn.baseline_tracker.confirmed_tick,
                "RTT_Ms": conn.rtt_ms,
            })

        manifest = {
            "SchemaVersion": "1.0.0",
            "UAF_Networking_System": "81.83",
            "SessionId": server.session.session_id,
            "ServerTick": server.server_tick,
            "WorldRevision": server.world_revision,
            "TickRate": server.session.tick_rate,
            "UE5_NetDriver": {
                "DriverClass": "/Script/OnlineSubsystemUtils.IpNetDriver",
                "MaxClientRate": 100000,
                "ConnectionCount": len(clients_data),
                "Connections": clients_data,
            },
            "UE5_ReplicationGraph": {
                "ActorCount": len(replicated_actors),
                "Actors": replicated_actors,
            },
        }

        # Canonical SHA-256 manifest hash
        manifest_raw = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        manifest["ManifestHash"] = hashlib.sha256(manifest_raw.encode("utf-8")).hexdigest()
        return manifest
