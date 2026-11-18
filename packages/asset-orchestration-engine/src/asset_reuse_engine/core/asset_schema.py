import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .asset_status import AssetState, ReuseDecisionType

@dataclass
class AssetMetadata:
    category: str # BUILDING, WEAPON, PROP, VEHICLE
    type_name: str # house, sword, tower
    style: str # medieval_stylized, realistic, futuristic
    dimensions: Dict[str, float] = field(default_factory=dict) # width, length, height
    materials: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    polycount: int = 1000

@dataclass
class LibraryAssetRecord:
    asset_id: str
    name: str
    metadata: AssetMetadata
    state: AssetState = AssetState.VALIDATED
    version: int = 1
    quality_score: float = 0.95
    failure_count: int = 0
    success_count: int = 0
    geometry_fingerprint: str = ""
    is_canonical: bool = False
    created_at: float = field(default_factory=time.time)

@dataclass
class AssetVariant:
    variant_id: str
    parent_asset_id: str
    parameter_overrides: Dict[str, Any] = field(default_factory=dict)
    variant_hash: str = ""
    created_at: float = field(default_factory=time.time)

@dataclass
class ReuseDecision:
    decision: ReuseDecisionType
    selected_asset_id: Optional[str]
    variant_id: Optional[str] = None
    confidence: float = 0.95
    reasons: List[str] = field(default_factory=list)
    score_breakdown: Dict[str, float] = field(default_factory=dict)
