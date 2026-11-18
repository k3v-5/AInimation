"""
CapabilityGapReport identifies when requested specifications exceed available generator capabilities.
UAF-81.1 Sections 64, 65, 66.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...capabilities.capability_registry import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityGapReport:
    """
    Structured report comparing required capabilities to available engine capabilities.
    """
    is_supported: bool
    requested_capabilities: List[str]
    available_capabilities: List[str]
    missing_capabilities: List[str]
    asset_id: Optional[str] = None
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_supported": self.is_supported,
            "requested_capabilities": self.requested_capabilities,
            "available_capabilities": self.available_capabilities,
            "missing_capabilities": self.missing_capabilities,
            "asset_id": self.asset_id,
            "rationale": self.rationale,
        }

    @classmethod
    def evaluate(
        cls,
        required_capabilities: List[str],
        registry: CapabilityRegistry,
        asset_id: Optional[str] = None,
    ) -> "CapabilityGapReport":
        """
        Compares requested capabilities against capability IDs registered in the CapabilityRegistry.
        """
        available = set(registry.list_keys())
        # Also check operations inside registered capability descriptions
        for cap_desc in registry.list():
            available.add(cap_desc.capability_id)
            for op in cap_desc.operations:
                available.add(op.value.lower())

        missing = [req for req in required_capabilities if req not in available]
        is_supported = len(missing) == 0

        rationale = (
            "All required capabilities are available in the engine registry."
            if is_supported
            else f"Missing {len(missing)} required capabilities: {', '.join(missing)}"
        )

        return cls(
            is_supported=is_supported,
            requested_capabilities=required_capabilities,
            available_capabilities=sorted(list(available)),
            missing_capabilities=missing,
            asset_id=asset_id,
            rationale=rationale,
        )
