"""
RuntimeAssetPackage encapsulates complete, production-ready assets for Unreal Engine.
UAF-81.8 Sections 3, 96, 97.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..graph.assembly_graph import AssetAssemblyGraph
from ..spatial.pivot import PivotDefinition
from ..spatial.socket import RuntimeSocketDefinition
from ..optimization.lod_policy import LODChain, NanitePolicy
from ..validation.runtime_validator import RuntimeAssetQualityReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class RuntimeAssetPackage:
    asset_id: str
    graph: AssetAssemblyGraph
    pivot: PivotDefinition
    sockets: List[RuntimeSocketDefinition] = field(default_factory=list)
    lod_chain: Optional[LODChain] = None
    nanite_policy: NanitePolicy = NanitePolicy.AUTO
    quality_report: Optional[RuntimeAssetQualityReport] = None
    version: str = "1.0.0"

    @property
    def build_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "graph": self.graph.to_dict(),
            "pivot": self.pivot.to_dict(),
            "sockets": [s.to_dict() for s in self.sockets],
            "lod_chain": self.lod_chain.to_dict() if self.lod_chain else None,
            "nanite_policy": self.nanite_policy.value,
            "quality_report": self.quality_report.to_dict() if self.quality_report else None,
            "version": self.version,
        }
