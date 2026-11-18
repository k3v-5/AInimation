"""
Strategy scoring and decision trace models for explainable selection.
UAF-81.2 Sections 27, 28, 29, 30.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass(frozen=True)
class StrategyScore:
    """
    Multi-dimensional evaluation score avoiding single opaque score dependency.
    """
    quality_score: float
    compatibility_score: float
    reliability_score: float
    determinism_score: float
    cost_score: float
    risk_score: float
    confidence: float = 1.0

    @property
    def aggregate_score(self) -> float:
        # Configurable weighted combination
        # Benefits: quality (0.35), compatibility (0.25), reliability (0.15), determinism (0.10)
        # Penalties: cost (0.10), risk (0.05)
        raw = (
            (self.quality_score * 0.35)
            + (self.compatibility_score * 0.25)
            + (self.reliability_score * 0.15)
            + (self.determinism_score * 0.10)
            - (self.cost_score * 0.10)
            - (self.risk_score * 0.05)
        )
        return max(0.0, min(1.0, round(raw, 4)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quality_score": self.quality_score,
            "compatibility_score": self.compatibility_score,
            "reliability_score": self.reliability_score,
            "determinism_score": self.determinism_score,
            "cost_score": self.cost_score,
            "risk_score": self.risk_score,
            "aggregate_score": self.aggregate_score,
            "confidence": self.confidence,
        }


@dataclass
class CandidateEvaluation:
    strategy_id: str
    is_eligible: bool
    score: Optional[StrategyScore] = None
    missing_hard_capabilities: List[str] = field(default_factory=list)
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "is_eligible": self.is_eligible,
            "score": self.score.to_dict() if self.score else None,
            "missing_hard_capabilities": self.missing_hard_capabilities,
            "rejection_reason": self.rejection_reason,
        }


@dataclass
class StrategyDecisionTrace:
    """
    Audit log explaining why a strategy was accepted or rejected.
    """
    asset_id: str
    target_profile: str
    quality_profile: str
    candidates: List[CandidateEvaluation] = field(default_factory=list)
    selected_strategy_id: Optional[str] = None
    selection_rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "target_profile": self.target_profile,
            "quality_profile": self.quality_profile,
            "candidates": [c.to_dict() for c in self.candidates],
            "selected_strategy_id": self.selected_strategy_id,
            "selection_rationale": self.selection_rationale,
        }
