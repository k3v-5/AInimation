from typing import List, Set
from .capability_schema import CapabilityType, CapabilityRegistry

class CapabilityResolver:
    @staticmethod
    def resolve_hierarchy(
        requested: List[CapabilityType],
        registry: CapabilityRegistry
    ) -> List[CapabilityType]:
        resolved: List[CapabilityType] = []
        seen: Set[CapabilityType] = set()

        def _resolve(cap: CapabilityType):
            defn = registry.get(cap)
            if defn:
                for req in defn.required_capabilities:
                    if req not in seen:
                        _resolve(req)
            if cap not in seen:
                seen.add(cap)
                resolved.append(cap)

        for c in requested:
            _resolve(c)

        return resolved
