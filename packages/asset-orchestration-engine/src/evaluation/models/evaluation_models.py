import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.evaluation_types import (
    EvaluationDimension, DefectSeverity, DefectStatus, BenchmarkStatus, AcceptanceDecision
)

@dataclass
class EvaluationDefect:
    defect_id: str
    category: str
    severity: DefectSeverity
    dimension: EvaluationDimension
    description: str
    location: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: str = "BENCHMARK_ENGINE"
    blocking: bool = False
    status: DefectStatus = DefectStatus.DETECTED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "defect_id": self.defect_id,
            "category": self.category,
            "severity": self.severity.value,
            "dimension": self.dimension.value,
            "description": self.description,
            "location": self.location,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "source": self.source,
            "blocking": self.blocking,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationDefect":
        return cls(
            defect_id=data["defect_id"],
            category=data.get("category", "GENERAL"),
            severity=DefectSeverity(data.get("severity", "MINOR")),
            dimension=EvaluationDimension(data.get("dimension", "GEOMETRY")),
            description=data.get("description", ""),
            location=data.get("location"),
            evidence=data.get("evidence", {}),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "BENCHMARK_ENGINE"),
            blocking=data.get("blocking", False),
            status=DefectStatus(data.get("status", "DETECTED"))
        )

@dataclass
class DimensionScore:
    dimension: EvaluationDimension
    score: float = 0.0          # [0.0, 1.0]
    weight: float = 1.0
    weighted_score: float = 0.0
    confidence: float = 1.0     # [0.0, 1.0]
    status: str = "MEASURED"
    evidence: Dict[str, Any] = field(default_factory=dict)
    defects: List[EvaluationDefect] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "score": round(self.score, 4),
            "weight": round(self.weight, 4),
            "weighted_score": round(self.weighted_score, 4),
            "confidence": round(self.confidence, 4),
            "status": self.status,
            "evidence": self.evidence,
            "defects": [d.to_dict() for d in self.defects]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DimensionScore":
        return cls(
            dimension=EvaluationDimension(data["dimension"]),
            score=data.get("score", 0.0),
            weight=data.get("weight", 1.0),
            weighted_score=data.get("weighted_score", 0.0),
            confidence=data.get("confidence", 1.0),
            status=data.get("status", "MEASURED"),
            evidence=data.get("evidence", {}),
            defects=[EvaluationDefect.from_dict(d) for d in data.get("defects", [])]
        )

@dataclass
class EvaluationProfile:
    profile_id: str
    name: str
    version: str = "1.0.0"
    dimension_weights: Dict[EvaluationDimension, float] = field(default_factory=dict)
    minimum_global_score: float = 0.80
    minimum_dimension_scores: Dict[EvaluationDimension, float] = field(default_factory=dict)
    critical_dimensions: List[EvaluationDimension] = field(default_factory=list)
    maximum_allowed_defects: int = 10
    maximum_critical_defects: int = 0
    minimum_confidence: float = 0.70

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "version": self.version,
            "dimension_weights": {k.value: v for k, v in self.dimension_weights.items()},
            "minimum_global_score": self.minimum_global_score,
            "minimum_dimension_scores": {k.value: v for k, v in self.minimum_dimension_scores.items()},
            "critical_dimensions": [d.value for d in self.critical_dimensions],
            "maximum_allowed_defects": self.maximum_allowed_defects,
            "maximum_critical_defects": self.maximum_critical_defects,
            "minimum_confidence": self.minimum_confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationProfile":
        return cls(
            profile_id=data["profile_id"],
            name=data.get("name", "Default Profile"),
            version=data.get("version", "1.0.0"),
            dimension_weights={EvaluationDimension(k): v for k, v in data.get("dimension_weights", {}).items()},
            minimum_global_score=data.get("minimum_global_score", 0.80),
            minimum_dimension_scores={EvaluationDimension(k): v for k, v in data.get("minimum_dimension_scores", {}).items()},
            critical_dimensions=[EvaluationDimension(d) for d in data.get("critical_dimensions", [])],
            maximum_allowed_defects=data.get("maximum_allowed_defects", 10),
            maximum_critical_defects=data.get("maximum_critical_defects", 0),
            minimum_confidence=data.get("minimum_confidence", 0.70)
        )

@dataclass
class EvaluationBenchmark:
    benchmark_id: str
    benchmark_version: str = "1.0.0"
    project_id: str = "DarX"
    asset_semantic_id: str = "asset.default"
    candidate_id: str = "candidate.v1"
    reference_id: Optional[str] = None
    baseline_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    status: BenchmarkStatus = BenchmarkStatus.DRAFT
    evaluation_profile: EvaluationProfile = field(default_factory=lambda: EvaluationProfile("DEFAULT", "Default Profile"))
    metrics: Dict[str, Any] = field(default_factory=dict)
    dimension_scores: Dict[EvaluationDimension, DimensionScore] = field(default_factory=dict)
    weighted_score: float = 0.0
    confidence: float = 1.0
    acceptance: AcceptanceDecision = AcceptanceDecision.REJECTED
    defects: List[EvaluationDefect] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    job_id: Optional[str] = None
    agent_id: Optional[str] = None
    graph_snapshot_id: Optional[str] = None
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self.compute_hash()

    def compute_hash(self) -> str:
        data = {
            "benchmark_id": self.benchmark_id,
            "benchmark_version": self.benchmark_version,
            "project_id": self.project_id,
            "asset_semantic_id": self.asset_semantic_id,
            "candidate_id": self.candidate_id,
            "reference_id": self.reference_id,
            "baseline_id": self.baseline_id,
            "weighted_score": round(self.weighted_score, 4),
            "confidence": round(self.confidence, 4),
            "acceptance": self.acceptance.value,
            "metrics": self.metrics,
            "dimension_scores": {k.value: v.to_dict() for k, v in self.dimension_scores.items()}
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.content_hash

    def calculate_global_score(self):
        total_weight = 0.0
        weighted_sum = 0.0
        conf_sum = 0.0
        count = 0

        # Collect all defects across dimensions
        self.defects = []

        for dim, dim_score in self.dimension_scores.items():
            w = self.evaluation_profile.dimension_weights.get(dim, dim_score.weight)
            dim_score.weight = w
            dim_score.weighted_score = dim_score.score * w
            weighted_sum += dim_score.weighted_score
            total_weight += w
            conf_sum += dim_score.confidence
            count += 1
            self.defects.extend(dim_score.defects)

        if total_weight > 0.0:
            self.weighted_score = weighted_sum / total_weight
        else:
            self.weighted_score = 0.0

        self.confidence = (conf_sum / count) if count > 0 else 1.0

        # Evaluate Acceptance Criteria
        critical_defects_count = sum(1 for d in self.defects if d.severity == DefectSeverity.CRITICAL or d.blocking)
        total_defects_count = len(self.defects)

        is_approved = True
        if self.weighted_score < self.evaluation_profile.minimum_global_score:
            is_approved = False
        if critical_defects_count > self.evaluation_profile.maximum_critical_defects:
            is_approved = False
        if total_defects_count > self.evaluation_profile.maximum_allowed_defects:
            is_approved = False
        if self.confidence < self.evaluation_profile.minimum_confidence:
            is_approved = False

        # Critical dimensions check
        for crit_dim in self.evaluation_profile.critical_dimensions:
            dim_res = self.dimension_scores.get(crit_dim)
            min_score = self.evaluation_profile.minimum_dimension_scores.get(crit_dim, 0.70)
            if not dim_res or dim_res.score < min_score:
                is_approved = False
                break

        self.acceptance = AcceptanceDecision.APPROVED if is_approved else AcceptanceDecision.REJECTED
        self.content_hash = self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "benchmark_version": self.benchmark_version,
            "project_id": self.project_id,
            "asset_semantic_id": self.asset_semantic_id,
            "candidate_id": self.candidate_id,
            "reference_id": self.reference_id,
            "baseline_id": self.baseline_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "status": self.status.value,
            "evaluation_profile": self.evaluation_profile.to_dict(),
            "metrics": self.metrics,
            "dimension_scores": {k.value: v.to_dict() for k, v in self.dimension_scores.items()},
            "weighted_score": round(self.weighted_score, 4),
            "confidence": round(self.confidence, 4),
            "acceptance": self.acceptance.value,
            "defects": [d.to_dict() for d in self.defects],
            "evidence": self.evidence,
            "provenance": self.provenance,
            "job_id": self.job_id,
            "agent_id": self.agent_id,
            "graph_snapshot_id": self.graph_snapshot_id,
            "content_hash": self.content_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationBenchmark":
        profile = EvaluationProfile.from_dict(data.get("evaluation_profile", {}))
        dim_scores = {
            EvaluationDimension(k): DimensionScore.from_dict(v)
            for k, v in data.get("dimension_scores", {}).items()
        }
        return cls(
            benchmark_id=data["benchmark_id"],
            benchmark_version=data.get("benchmark_version", "1.0.0"),
            project_id=data.get("project_id", "DarX"),
            asset_semantic_id=data.get("asset_semantic_id", "asset.default"),
            candidate_id=data.get("candidate_id", "candidate.v1"),
            reference_id=data.get("reference_id"),
            baseline_id=data.get("baseline_id"),
            created_at=data.get("created_at", time.time()),
            completed_at=data.get("completed_at"),
            status=BenchmarkStatus(data.get("status", "DRAFT")),
            evaluation_profile=profile,
            metrics=data.get("metrics", {}),
            dimension_scores=dim_scores,
            weighted_score=data.get("weighted_score", 0.0),
            confidence=data.get("confidence", 1.0),
            acceptance=AcceptanceDecision(data.get("acceptance", "REJECTED")),
            defects=[EvaluationDefect.from_dict(d) for d in data.get("defects", [])],
            evidence=data.get("evidence", {}),
            provenance=data.get("provenance", {}),
            job_id=data.get("job_id"),
            agent_id=data.get("agent_id"),
            graph_snapshot_id=data.get("graph_snapshot_id"),
            content_hash=data.get("content_hash", "")
        )
