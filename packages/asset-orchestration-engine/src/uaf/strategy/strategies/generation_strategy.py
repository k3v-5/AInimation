"""
GenerationStrategy models high-level approach for asset fabrication.
UAF-81.2 Sections 16, 18, 27, 28.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.identity.asset_types import AssetType
from .strategy_category import StrategyCategory, DeterminismMode


@dataclass(frozen=True)
class GenerationStrategy:
    """
    Formal blueprint strategy declaring required capabilities, categories, and cost/quality trade-offs.
    """
    strategy_id: str
    name: str
    category: StrategyCategory
    version: str = "1.0.0"
    description: str = ""
    supported_assets: List[AssetType] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)  # HARD requirements
    optional_capabilities: List[str] = field(default_factory=list)  # SOFT requirements
    constraints: Dict[str, Any] = field(default_factory=dict)
    quality_rating: float = 0.5  # 0.0 to 1.0
    cost_rating: float = 0.5     # 0.0 to 1.0 (higher = more expensive)
    risk_rating: float = 0.2     # 0.0 to 1.0 (higher = riskier)
    determinism: DeterminismMode = DeterminismMode.SEEDED_DETERMINISTIC
    supported_complexities: List[str] = field(default_factory=lambda: ["C0", "C1", "C2", "C3", "C4", "C5"])
    pipeline_node_templates: List[Dict[str, Any]] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "category": self.category.value,
            "version": self.version,
            "description": self.description,
            "supported_assets": [at.value for at in self.supported_assets],
            "required_capabilities": self.required_capabilities,
            "optional_capabilities": self.optional_capabilities,
            "constraints": self.constraints,
            "quality_rating": self.quality_rating,
            "cost_rating": self.cost_rating,
            "risk_rating": self.risk_rating,
            "determinism": self.determinism.value,
            "supported_complexities": self.supported_complexities,
            "pipeline_node_templates": self.pipeline_node_templates,
        }
