from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class AssetSearchQuery:
    type_name: str # house, sword
    style: Optional[str] = None # medieval_stylized
    target_dimensions: Dict[str, float] = field(default_factory=dict)
    reference_visual_score: Optional[float] = None
    allow_parametric_variant: bool = True
    tags: List[str] = field(default_factory=list)

@dataclass
class SearchResultCandidate:
    asset_id: str
    semantic_score: float
    visual_score: float
    style_score: float
    dimension_score: float
    quality_score: float
    reuse_score: float
    reasons: List[str] = field(default_factory=list)
