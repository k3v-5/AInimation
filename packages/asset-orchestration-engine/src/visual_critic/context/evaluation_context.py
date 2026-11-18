from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...spec_compiler.core.asset_spec import AssetSpec

@dataclass
class EvaluationContext:
    asset_id: str
    generation_id: str
    template_id: str
    template_version: str
    asset_spec: AssetSpec
    resolved_parameters: Dict[str, Any] = field(default_factory=dict)
    technical_validation: Dict[str, Any] = field(default_factory=dict)
    visual_views: List[str] = field(default_factory=list) # e.g. FRONT, HERO, THREE_QUARTER
    iteration_number: int = 1
    iteration_budget: int = 5
    protected_parameters: List[str] = field(default_factory=list)
