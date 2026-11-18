from typing import Dict, Any, List, Optional
from ..core.golden_types import GoldenStatus, ReferenceStatus, VersionBumpType, ComparisonOutcome
from ..core.golden_exceptions import GoldenAssetException, GoldenIntegrityError, GoldenPromotionError
from ..models.golden_asset import GoldenAsset
from ..models.golden_baseline import GoldenBaseline
from ..models.reference_asset import ReferenceAsset
from ..persistence.golden_store import GoldenAssetStore
from ..validation.golden_validator import GoldenValidator
from ..promotion.promotion_engine import PromotionEngine
from ..promotion.demotion_engine import DemotionEngine
from ..comparison.golden_comparator import GoldenComparator, GoldenComparisonResult
from ..governance.golden_governance_guard import GoldenGovernanceGuard
from ..integration.knowledge_graph_bridge import GoldenKnowledgeGraphBridge
from ...evaluation import EvaluationBenchmark

class GoldenAssetAPI:
    """
    Unified public facade for the Golden Asset & Baseline Reference Library (Phase 76).
    """
    def __init__(self, persistence_path: Optional[str] = None):
        self.store = GoldenAssetStore(persistence_path)
        self.promotion = PromotionEngine(self.store)
        self.demotion = DemotionEngine(self.store)
        self.governance = GoldenGovernanceGuard()
        self.kg_bridge = GoldenKnowledgeGraphBridge()

    def register_reference_asset(
        self,
        reference_id: str,
        semantic_id: str,
        asset_family: str = "weapon",
        category: str = "rifle",
        metadata: Optional[Dict[str, Any]] = None,
        source_file: Optional[str] = None,
        agent_id: str = "agent.strategy"
    ) -> ReferenceAsset:
        self.governance.validate_operation(agent_id, "MODIFY_REFERENCE")
        ref = ReferenceAsset(
            reference_id=reference_id,
            semantic_id=semantic_id,
            asset_family=asset_family,
            category=category,
            metadata=metadata or {},
            source_file=source_file
        )
        return self.store.store_reference_asset(ref)

    def get_reference_asset(self, reference_id: str) -> Optional[ReferenceAsset]:
        return self.store.get_reference_asset(reference_id)

    def list_reference_assets(self) -> List[ReferenceAsset]:
        return self.store.list_reference_assets()

    def create_baseline(
        self,
        baseline_id: str,
        golden_asset_id: str,
        version: str = "1.0.0",
        metrics: Optional[Dict[str, Any]] = None,
        dimension_scores: Optional[Dict[str, float]] = None,
        global_score: float = 0.0,
        defects: Optional[List[Dict[str, Any]]] = None,
        evaluation_id: str = "",
        agent_id: str = "agent.visual.critic"
    ) -> GoldenBaseline:
        self.governance.validate_operation(agent_id, "CREATE_BASELINE")
        baseline = GoldenBaseline(
            baseline_id=baseline_id,
            golden_asset_id=golden_asset_id,
            version=version,
            metrics=metrics or {},
            dimension_scores=dimension_scores or {},
            global_score=global_score,
            defects=defects or [],
            evaluation_id=evaluation_id
        )
        saved = self.store.store_baseline(baseline)
        try:
            self.kg_bridge.sync_baseline_to_graph(saved, agent_id=agent_id)
        except Exception as e:
            print(f"[GoldenAssetAPI] Note syncing baseline to graph: {e}")
        return saved

    def get_baseline(self, baseline_id: str) -> Optional[GoldenBaseline]:
        return self.store.get_baseline(baseline_id)

    def list_baselines(self, golden_asset_id: Optional[str] = None) -> List[GoldenBaseline]:
        all_b = self.store.list_baselines()
        if golden_asset_id:
            return [b for b in all_b if b.golden_asset_id == golden_asset_id]
        return all_b

    def evaluate_for_promotion(self, benchmark: EvaluationBenchmark, min_global_score: float = 0.85) -> List[str]:
        return GoldenValidator.validate_for_promotion(benchmark, min_global_score=min_global_score)

    def promote_to_golden(
        self,
        golden_asset_id: str,
        semantic_id: str,
        benchmark: EvaluationBenchmark,
        asset_family: str = "weapon",
        category: str = "rifle",
        bump_type: Optional[VersionBumpType] = None,
        approved_by: str = "agent.visual.critic",
        notes: str = "Initial Golden release",
        min_global_score: float = 0.85
    ) -> GoldenAsset:
        self.governance.validate_operation(approved_by, "PROMOTE_ASSET")
        golden = self.promotion.promote_candidate(
            golden_asset_id=golden_asset_id,
            semantic_id=semantic_id,
            benchmark=benchmark,
            asset_family=asset_family,
            category=category,
            bump_type=bump_type,
            approved_by=approved_by,
            notes=notes,
            min_global_score=min_global_score
        )
        try:
            self.kg_bridge.sync_golden_asset_to_graph(golden, agent_id=approved_by)
        except Exception as e:
            print(f"[GoldenAssetAPI] Note syncing golden asset to graph: {e}")
        return golden

    def demote_golden(
        self,
        golden_asset_id: str,
        target_status: GoldenStatus,
        reason: str,
        actor: str = "agent.strategy",
        successor_id: Optional[str] = None
    ) -> GoldenAsset:
        self.governance.validate_operation(actor, "DEMOTE_ASSET")
        return self.demotion.demote_golden(
            golden_asset_id=golden_asset_id,
            target_status=target_status,
            reason=reason,
            actor=actor,
            successor_id=successor_id
        )

    def create_new_version(
        self,
        golden_asset_id: str,
        benchmark: EvaluationBenchmark,
        bump_type: VersionBumpType = VersionBumpType.MINOR,
        approved_by: str = "agent.visual.critic",
        notes: str = "Updated Golden version"
    ) -> GoldenAsset:
        existing = self.store.get_golden_asset(golden_asset_id)
        if not existing:
            raise KeyError(f"Golden Asset '{golden_asset_id}' not found.")
        return self.promote_to_golden(
            golden_asset_id=golden_asset_id,
            semantic_id=existing.semantic_id,
            benchmark=benchmark,
            asset_family=existing.asset_family,
            category=existing.category,
            bump_type=bump_type,
            approved_by=approved_by,
            notes=notes
        )

    def compare_against_golden(
        self,
        candidate_bench: EvaluationBenchmark,
        golden_asset_id: str,
        version: Optional[str] = None
    ) -> GoldenComparisonResult:
        golden = self.store.get_golden_asset(golden_asset_id)
        if not golden:
            raise KeyError(f"Golden Asset '{golden_asset_id}' not found.")
        v = version or golden.current_version
        baseline_id = golden.baselines.get(v)
        if not baseline_id:
            raise KeyError(f"No baseline associated with version '{v}' of golden asset '{golden_asset_id}'.")
        baseline = self.store.get_baseline(baseline_id)
        if not baseline:
            raise KeyError(f"Baseline '{baseline_id}' not found in store.")
        return GoldenComparator.compare(candidate_bench, baseline)

    def verify_golden_integrity(self, golden_asset_id: str) -> bool:
        asset = self.store.get_golden_asset(golden_asset_id)
        return asset.verify_integrity() if asset else False

    def get_golden_history(self, golden_asset_id: str) -> Dict[str, Any]:
        asset = self.store.get_golden_asset(golden_asset_id)
        if not asset:
            return {}
        return {
            "golden_asset_id": asset.golden_asset_id,
            "semantic_id": asset.semantic_id,
            "current_version": asset.current_version,
            "status": asset.status.value,
            "versions": {k: v.to_dict() for k, v in asset.versions.items()},
            "baselines": asset.baselines,
            "successor_id": asset.successor_id
        }

    def get_golden_successor(self, golden_asset_id: str) -> Optional[str]:
        asset = self.store.get_golden_asset(golden_asset_id)
        return asset.successor_id if asset else None

    def get_golden_asset(self, golden_asset_id: str) -> Optional[GoldenAsset]:
        return self.store.get_golden_asset(golden_asset_id)

    def list_golden_assets(self) -> List[GoldenAsset]:
        return self.store.list_golden_assets()
