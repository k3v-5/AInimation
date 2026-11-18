"""
UAF-81.82: Path Request Queue and Deterministic Path Invalidation.
"""

from __future__ import annotations

import heapq
from typing import List, Optional, Tuple

from ..models.definition import (
    NavigationProfile,
    PathRequest,
    PathResult,
    PathStatus,
)
from .mesh import NavMesh


class PathRequestQueue:
    """
    Deterministic priority queue for asynchronous / budgeted path requests.
    Ordered by: (-priority.value, requested_tick, agent_id, request_id)
    """

    def __init__(self):
        # Heap tuple: (neg_priority, requested_tick, agent_id, request_id, PathRequest)
        self._heap: List[Tuple[int, int, str, int, PathRequest]] = []

    def push(self, request: PathRequest) -> None:
        key = (-request.priority.value, request.requested_tick, request.agent_id, request.request_id, request)
        heapq.heappush(self._heap, key)

    def pop(self) -> Optional[PathRequest]:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[4]

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0


class PathValidator:
    """Validates whether a previously computed path remains topologically viable."""

    @staticmethod
    def is_path_valid(path_result: PathResult, nav_mesh: NavMesh, profile: NavigationProfile) -> bool:
        if path_result.status != PathStatus.SUCCESS or not path_result.polygons:
            return False

        poly_ids = path_result.polygons
        for pid in poly_ids:
            poly = nav_mesh.get_polygon(pid)
            if poly is None:
                return False
            if not profile.is_area_allowed(poly.area_type):
                return False

        # Verify connectivity between consecutive polygons
        for i in range(len(poly_ids) - 1):
            p_curr = nav_mesh.get_polygon(poly_ids[i])
            if p_curr is None or poly_ids[i + 1] not in p_curr.neighbors:
                return False

        return True
