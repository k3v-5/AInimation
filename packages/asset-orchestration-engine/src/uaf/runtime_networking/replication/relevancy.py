"""
UAF-81.83: Spatial Relevancy and Client Interest Filtering.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Set, Tuple

from ..models.definition import (
    InterestProfile,
    NetworkEntityId,
    ReplicationPolicy,
    Vec3,
    ensure_finite_vec3,
)


class SpatialRelevancyManager:
    """
    Evaluates entity relevancy for each client connection based on
    replication policies, ownership, and Euclidean distance to interest profiles.
    """

    def __init__(self):
        self._entity_policies: Dict[NetworkEntityId, ReplicationPolicy] = {}
        self._entity_owners: Dict[NetworkEntityId, Optional[str]] = {}
        self._entity_positions: Dict[NetworkEntityId, Vec3] = {}
        self._client_profiles: Dict[str, InterestProfile] = {}

    def register_entity(
        self,
        net_id: NetworkEntityId,
        policy: ReplicationPolicy = ReplicationPolicy.RELEVANT,
        owner_id: Optional[str] = None,
        position: Vec3 = (0.0, 0.0, 0.0),
    ) -> None:
        """Register or update an entity's relevancy parameters."""
        self._entity_policies[net_id] = policy
        self._entity_owners[net_id] = owner_id
        self._entity_positions[net_id] = ensure_finite_vec3(position, f"relevancy entity {net_id}")

    def unregister_entity(self, net_id: NetworkEntityId) -> None:
        """Remove an entity from relevancy tracking."""
        self._entity_policies.pop(net_id, None)
        self._entity_owners.pop(net_id, None)
        self._entity_positions.pop(net_id, None)

    def update_entity_position(self, net_id: NetworkEntityId, position: Vec3) -> None:
        """Update an entity's 3D spatial position."""
        if net_id in self._entity_policies:
            self._entity_positions[net_id] = ensure_finite_vec3(position, f"relevancy entity {net_id}")

    def set_client_interest(self, client_id: str, profile: InterestProfile) -> None:
        """Set the active interest center and view distance for a client."""
        self._client_profiles[client_id] = profile

    def remove_client(self, client_id: str) -> None:
        """Clean up client interest profile."""
        self._client_profiles.pop(client_id, None)

    def is_relevant(self, net_id: NetworkEntityId, client_id: str) -> bool:
        """Check if an individual entity is relevant to a given client."""
        policy = self._entity_policies.get(net_id, ReplicationPolicy.RELEVANT)

        if policy == ReplicationPolicy.ALWAYS:
            return True

        owner = self._entity_owners.get(net_id)
        if policy == ReplicationPolicy.OWNER_ONLY:
            return owner == client_id

        if policy == ReplicationPolicy.DORMANT:
            return False

        # Spatial distance check
        profile = self._client_profiles.get(client_id)
        if not profile:
            return False

        ent_pos = self._entity_positions.get(net_id, (0.0, 0.0, 0.0))
        dx = ent_pos[0] - profile.position[0]
        dy = ent_pos[1] - profile.position[1]
        dz = ent_pos[2] - profile.position[2]
        dist_sq = dx * dx + dy * dy + dz * dz

        return dist_sq <= (profile.radius * profile.radius)

    def get_relevant_entities(self, client_id: str) -> Set[NetworkEntityId]:
        """Compute the complete set of entities relevant to the given client."""
        relevant_set: Set[NetworkEntityId] = set()
        for net_id in self._entity_policies:
            if self.is_relevant(net_id, client_id):
                relevant_set.add(net_id)
        return relevant_set
