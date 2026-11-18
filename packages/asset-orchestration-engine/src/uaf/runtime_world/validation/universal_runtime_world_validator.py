"""
Universal Runtime World Validation Pipeline.
Complies with UAF-81.73 specification.
"""

from typing import List, Set, Tuple

from uaf.runtime_world.models.definition import (
    RuntimeWorld,
    WorldStateSnapshot,
    EntityLifecycleState,
    ComponentLifecycleState,
)


class UniversalRuntimeWorldValidator:
    """Normative validation suite for runtime world graphs, entity hierarchies, systems, and snapshots."""

    @staticmethod
    def validate_hierarchy(world: RuntimeWorld) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if world.root_entity_id not in world.entities:
            errors.append(f"ROOT_NOT_FOUND: Root entity '{world.root_entity_id}' not found in world.")
            return False, errors

        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(eid: str) -> bool:
            visited.add(eid)
            stack.add(eid)
            ent = world.entities[eid]
            for cid in ent.children_ids:
                if cid not in world.entities:
                    errors.append(f"CHILD_NOT_FOUND: Child '{cid}' referenced by '{eid}' does not exist.")
                    continue
                if cid in stack:
                    errors.append(f"NO_HIERARCHY_CYCLES: Cycle detected at '{cid}'.")
                    return False
                if cid not in visited:
                    if not dfs(cid):
                        return False
            stack.remove(eid)
            return True

        has_no_cycles = dfs(world.root_entity_id)

        # Check for orphans
        for eid in world.entities:
            if eid not in visited and eid != world.root_entity_id:
                errors.append(f"ORPHAN_ENTITY: Entity '{eid}' is not reachable from root.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_systems(world: RuntimeWorld) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        systems = world.systems
        graph = {sid: [] for sid in systems}
        in_degree = {sid: 0 for sid in systems}

        for sid, s in systems.items():
            for dep in s.dependencies:
                if dep in systems:
                    graph[dep].append(sid)
                    in_degree[sid] += 1

        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        visited_count = 0
        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for nxt in graph[curr]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if visited_count < len(systems):
            errors.append("NO_SYSTEM_DEPENDENCY_CYCLE: Cycle detected among registered systems.")

        return len(errors) == 0, errors

    @classmethod
    def validate_world(cls, world: RuntimeWorld) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not world.world_id or not world.world_id.strip():
            errors.append("EMPTY_WORLD_ID: World ID cannot be empty.")

        ok_hier, hier_errs = cls.validate_hierarchy(world)
        if not ok_hier:
            errors.extend(hier_errs)

        ok_sys, sys_errs = cls.validate_systems(world)
        if not ok_sys:
            errors.extend(sys_errs)

        # Validate component dependencies
        for eid, ent in world.entities.items():
            for cid, comp in ent.components.items():
                for dep in comp.dependencies:
                    if dep not in ent.components:
                        errors.append(f"MISSING_DEPENDENCY: Entity '{eid}' component '{cid}' missing '{dep}'.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_snapshot(snapshot: WorldStateSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not snapshot.snapshot_id or not snapshot.snapshot_id.strip():
            errors.append("EMPTY_SNAPSHOT_ID")
        expected_fp = snapshot.compute_fingerprint()
        if snapshot.fingerprint != expected_fp:
            errors.append(f"SNAPSHOT_FINGERPRINT_MISMATCH: Expected '{expected_fp}', got '{snapshot.fingerprint}'.")

        return len(errors) == 0, errors
