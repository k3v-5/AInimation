from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class RootCause:
    cause_id: str
    category: str
    description: str
    evidence_ids: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    confidence: float = 1.0 # [0.0, 1.0]
    alternatives: List[str] = field(default_factory=list)
    causal_chain: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cause_id": self.cause_id,
            "category": self.category,
            "description": self.description,
            "evidence_ids": self.evidence_ids,
            "affected_components": self.affected_components,
            "confidence": round(self.confidence, 4),
            "alternatives": self.alternatives,
            "causal_chain": self.causal_chain
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RootCause":
        return cls(
            cause_id=data["cause_id"],
            category=data.get("category", "GENERAL"),
            description=data.get("description", ""),
            evidence_ids=data.get("evidence_ids", []),
            affected_components=data.get("affected_components", []),
            confidence=data.get("confidence", 1.0),
            alternatives=data.get("alternatives", []),
            causal_chain=data.get("causal_chain", [])
        )

@dataclass
class DiagnosticReport:
    diagnosis_id: str
    failure_id: str
    root_cause: RootCause
    alternative_causes: List[RootCause] = field(default_factory=list)
    impacted_assets: List[str] = field(default_factory=list)
    invalidated_evaluations: List[str] = field(default_factory=list)
    recommended_action: str = "NO_ACTION"
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diagnosis_id": self.diagnosis_id,
            "failure_id": self.failure_id,
            "root_cause": self.root_cause.to_dict(),
            "alternative_causes": [c.to_dict() for c in self.alternative_causes],
            "impacted_assets": self.impacted_assets,
            "invalidated_evaluations": self.invalidated_evaluations,
            "recommended_action": self.recommended_action,
            "confidence": round(self.confidence, 4)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagnosticReport":
        return cls(
            diagnosis_id=data["diagnosis_id"],
            failure_id=data["failure_id"],
            root_cause=RootCause.from_dict(data["root_cause"]),
            alternative_causes=[RootCause.from_dict(c) for c in data.get("alternative_causes", [])],
            impacted_assets=data.get("impacted_assets", []),
            invalidated_evaluations=data.get("invalidated_evaluations", []),
            recommended_action=data.get("recommended_action", "NO_ACTION"),
            confidence=data.get("confidence", 1.0)
        )
