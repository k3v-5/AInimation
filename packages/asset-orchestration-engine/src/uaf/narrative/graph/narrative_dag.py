"""
UAF-81.98: Branching Narrative Directed Acyclic Graph (DAG) Engine.
Manages quest progression, validates acyclic dependency topology via Kahn's algorithm,
enforces mutually exclusive faction branches, and computes the critical story spine.
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple, Any

from ..core.contracts import (
    QuestDefinition,
    QuestState,
    QuestType,
)


class BranchingNarrativeDAG:
    """
    Directs quest network progression and guarantees mathematical acyclicity and consistency.
    """

    def __init__(self):
        self.quests: Dict[str, QuestDefinition] = {}

    def add_quest(self, quest: QuestDefinition) -> None:
        """Registers a quest definition into the graph."""
        self.quests[quest.quest_id] = quest

    def validate_acyclicity(self) -> Tuple[bool, List[str]]:
        """
        Validates that the quest prerequisite graph is strictly acyclic using Kahn's algorithm.
        Returns (is_acyclic, cycle_participating_ids).
        """
        in_degree: Dict[str, int] = {q_id: 0 for q_id in self.quests}
        adj: Dict[str, List[str]] = defaultdict(list)

        for q_id, q in self.quests.items():
            for prereq in q.prerequisite_quest_ids:
                if prereq in self.quests:
                    adj[prereq].append(q_id)
                    in_degree[q_id] += 1

        queue = deque([q_id for q_id, deg in in_degree.items() if deg == 0])
        visited_count = 0

        while queue:
            node = queue.popleft()
            visited_count += 1

            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        is_acyclic = visited_count == len(self.quests)
        cycle_nodes = [q_id for q_id, deg in in_degree.items() if deg > 0] if not is_acyclic else []

        return is_acyclic, cycle_nodes

    def get_topological_order(self) -> List[str]:
        """
        Computes a valid topological sort of all registered quests.
        Raises ValueError if a circular prerequisite cycle exists.
        """
        is_acyclic, cycle_nodes = self.validate_acyclicity()
        if not is_acyclic:
            raise ValueError(f"ERR_NARRATIVE_CYCLE_DETECTED: Circular dependencies among {cycle_nodes}")

        in_degree: Dict[str, int] = {q_id: 0 for q_id in self.quests}
        adj: Dict[str, List[str]] = defaultdict(list)

        for q_id, q in self.quests.items():
            for prereq in q.prerequisite_quest_ids:
                if prereq in self.quests:
                    adj[prereq].append(q_id)
                    in_degree[q_id] += 1

        queue = deque([q_id for q_id, deg in in_degree.items() if deg == 0])
        order: List[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)

            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return order

    def resolve_faction_branch_commitment(
        self,
        committed_quest_id: str,
        current_states: Dict[str, QuestState],
    ) -> Dict[str, QuestState]:
        """
        Transitions mutually exclusive antagonist quests into ABANDONED / FAILED states.
        """
        new_states = dict(current_states)
        quest = self.quests.get(committed_quest_id)
        if not quest:
            return new_states

        new_states[committed_quest_id] = QuestState.ACTIVE

        for exclusive_id in quest.mutually_exclusive_quest_ids:
            if exclusive_id in new_states:
                # Cancel or fail antagonistic quest
                new_states[exclusive_id] = QuestState.ABANDONED

        return new_states

    def get_available_quests(
        self,
        completed_ids: Set[str],
        current_states: Dict[str, QuestState],
    ) -> List[QuestDefinition]:
        """
        Returns all quests whose prerequisites are met and have not yet been started or blocked.
        """
        available: List[QuestDefinition] = []

        for q_id, q in self.quests.items():
            state = current_states.get(q_id, QuestState.NOT_STARTED)
            if state != QuestState.NOT_STARTED:
                continue

            # Check all prerequisites are satisfied
            prereqs_met = all(prereq in completed_ids for prereq in q.prerequisite_quest_ids)
            if prereqs_met:
                available.append(q)

        return available

    def compute_critical_path(self) -> List[str]:
        """
        Calculates the longest path of prerequisite dependencies, representing the core narrative spine.
        """
        order = self.get_topological_order()
        dist: Dict[str, int] = {q_id: 1 for q_id in order}
        parent: Dict[str, Optional[str]] = {q_id: None for q_id in order}

        adj: Dict[str, List[str]] = defaultdict(list)
        for q_id, q in self.quests.items():
            for prereq in q.prerequisite_quest_ids:
                if prereq in self.quests:
                    adj[prereq].append(q_id)

        for u in order:
            for v in adj[u]:
                if dist[u] + 1 > dist[v]:
                    dist[v] = dist[u] + 1
                    parent[v] = u

        # Find max dist node
        max_node = max(dist.keys(), key=lambda k: dist[k]) if dist else None
        if not max_node:
            return []

        path = []
        curr = max_node
        while curr:
            path.append(curr)
            curr = parent[curr]

        path.reverse()
        return path
