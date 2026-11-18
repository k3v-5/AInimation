"""
FabricatedCharacterPackage encapsulates complete multi-layered character fabrication data.
UAF-81.10 Sections 156, 158, 165.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..anatomy.proportions import ProportionProfile
from ..anatomy.body_graph import SemanticBodyGraph
from ..garments.garment import GarmentDefinition
from ..generator.character_fabricator import TopologyStrategyType, FabricationQuality
from ..validation.fabrication_validator import FabricationValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class FabricatedCharacterPackage:
    asset_id: str
    archetype_name: str
    body_graph: SemanticBodyGraph
    proportions: ProportionProfile
    garments: List[GarmentDefinition] = field(default_factory=list)
    topology_strategy: TopologyStrategyType = TopologyStrategyType.HYBRID
    quality_level: FabricationQuality = FabricationQuality.HIGH
    validation_report: Optional[FabricationValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "archetype_name": self.archetype_name,
            "body_graph": self.body_graph.to_dict(),
            "proportions": self.proportions.to_dict(),
            "garments": [g.to_dict() for g in self.garments],
            "topology_strategy": self.topology_strategy.value,
            "quality_level": self.quality_level.value,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
