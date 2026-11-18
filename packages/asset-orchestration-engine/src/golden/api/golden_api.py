from typing import Dict, Any, List, Optional, Tuple
from ..core.golden_types import (
    GoldenAssetStatus, MutationType, RegressionLevel, GoldenAssetException,
    GoldenImmutabilityError, GoldenIntegrityError, GoldenDuplicateError, GoldenAuthorizationError
)
from ..core.golden_models import GoldenAsset
from ..core.golden_identity import GoldenIdentityHelper
from ..fingerprint.asset_fingerprint import AssetFingerprinter
from ..registry.golden_registry import GoldenRegistry
from ..registry.version_registry import VersionRegistry
from ..storage.golden_store import GoldenStore
from ..storage.manifest_store import ManifestStore
from ..storage.integrity_store import IntegrityStore
from ..comparison.golden_comparator import GoldenComparator, GoldenComparisonResult
from ..comparison.regression_policy import RegressionPolicy
from ..comparison.compatibility_checker import CompatibilityChecker
from ..protection.immutability_guard import ImmutabilityGuard
from ..protection.mutation_detector import MutationDetector
from ..protection.authorization_guard import AuthorizationGuard
from ..integration.evaluation_bridge import EvaluationBridge
from ..integration.knowledge_graph_bridge import KnowledgeGraphBridge
from ..integration.recovery_bridge import RecoveryBridge
from ...evaluation import EvaluationBenchmark

class GoldenAPI:
    """
    Unified public facade for Golden Assets & Baseline Reference Library (Phase 76).
    """
    def __init__(self, persistence_path: Optional[str] = None):
        self.store = GoldenStore(persistence_path)
        self.registry = GoldenRegistry()
        self.versions = VersionRegistry()
        self.auth = AuthorizationGuard()
        self.kg_bridge = KnowledgeGraphBridge()
        self.recovery = RecoveryBridge(self.store)

        # Ingest stored assets into registry and version tracker
        for a in self.store.list_all():
            self.registry.register(a, allow_update=True)
            self.versions.register_version(a)

    def create_golden(
        self,
        semantic_id: str,
        asset_name: str,
        asset_data: Dict[str, Any],
        benchmark: EvaluationBenchmark,
        version: int = 1,
        asset_type: str = "weapon",
        agent_id: str = "agent.strategy",
        metadata: Optional[Dict[str, Any]] = None
    ) -> GoldenAsset:
        self.auth.check_permission(agent_id, "CREATE_GOLDEN")
        golden_id = GoldenIdentityHelper.generate_golden_id(semantic_id, version)

        # Compute fingerprints
        fps = AssetFingerprinter.compute_all(asset_data)

        # Create Draft Asset
        asset = GoldenAsset(
            golden_id=golden_id,
            semantic_id=semantic_id,
            asset_name=asset_name,
            asset_type=asset_type,
            version=version,
            created_by=agent_id,
            status=GoldenAssetStatus.DRAFT,
            fingerprint=fps,
            evaluation_id=benchmark.benchmark_id,
            baseline_score=benchmark.weighted_score,
            minimum_acceptable_score=0.85,
            metadata=metadata or {}
        )
        return self.store.store_golden(asset, allow_update=True)

    def validate_golden(self, asset: GoldenAsset, benchmark: EvaluationBenchmark) -> List[str]:
        errors = EvaluationBridge.validate_benchmark_for_golden(benchmark, min_score=asset.minimum_acceptable_score)
        if not asset.verify_integrity():
            errors.append("Manifest hash mismatch in Golden Asset.")
        return errors

    def activate_golden(
        self,
        golden_id: str,
        benchmark: EvaluationBenchmark,
        agent_id: str = "agent.strategy"
    ) -> GoldenAsset:
        self.auth.check_permission(agent_id, "ACTIVATE_GOLDEN")
        asset = self.get_golden(golden_id)
        if not asset:
            raise KeyError(f"Golden Asset '{golden_id}' not found.")

        # Validate
        errors = self.validate_golden(asset, benchmark)
        if errors:
            raise GoldenAssetException(f"Cannot activate Golden Asset: {'; '.join(errors)}")

        self.recovery.begin_checkpoint()
        try:
            asset.status = GoldenAssetStatus.ACTIVE
            saved = self.store.store_golden(asset, allow_update=True)
            self.registry.register(saved, allow_update=True)
            self.versions.register_version(saved)
            self.recovery.commit_checkpoint()

            try:
                self.kg_bridge.sync_golden(saved, agent_id=agent_id)
            except Exception as e:
                print(f"[GoldenAPI] Note syncing to graph: {e}")

            return saved
        except Exception:
            self.recovery.rollback_to_checkpoint()
            raise

    def get_golden(self, golden_id: str) -> Optional[GoldenAsset]:
        return self.store.get_golden(golden_id)

    def get_active_golden(self, semantic_id: str) -> Optional[GoldenAsset]:
        return self.versions.get_active_version(semantic_id)

    def list_versions(self, semantic_id: str) -> List[GoldenAsset]:
        return self.versions.get_versions(semantic_id)

    def compare_with_golden(
        self,
        candidate_bench: EvaluationBenchmark,
        golden_id: str,
        policy: Optional[RegressionPolicy] = None
    ) -> GoldenComparisonResult:
        golden = self.get_golden(golden_id)
        if not golden:
            raise KeyError(f"Golden Asset '{golden_id}' not found.")
        compat_errors = CompatibilityChecker.check_compatibility(candidate_bench, golden)
        if compat_errors:
            raise GoldenAssetException(f"Compatibility check failed: {'; '.join(compat_errors)}")

        return GoldenComparator.compare(candidate_bench, golden, policy=policy)

    def verify_integrity(self, golden_id: str) -> bool:
        asset = self.get_golden(golden_id)
        return asset.verify_integrity() if asset else False

    def supersede_golden(
        self,
        old_golden_id: str,
        new_golden: GoldenAsset,
        benchmark: EvaluationBenchmark,
        agent_id: str = "agent.strategy"
    ) -> GoldenAsset:
        self.auth.check_permission(agent_id, "SUPERSEDE_GOLDEN")
        old_asset = self.get_golden(old_golden_id)
        if not old_asset:
            raise KeyError(f"Old Golden Asset '{old_golden_id}' not found.")

        # Update parent link and recalculate manifest
        new_golden.parent_golden_id = old_asset.golden_id
        self.store.store_golden(new_golden, allow_update=True)

        # Activate new
        activated = self.activate_golden(new_golden.golden_id, benchmark, agent_id=agent_id)
        
        # Supersede old
        old_asset.status = GoldenAssetStatus.SUPERSEDED
        self.store.store_golden(old_asset, allow_update=True)
        self.versions.supersede_version(old_asset, activated)

        return activated

    def revoke_golden(self, golden_id: str, reason: str, agent_id: str = "agent.strategy") -> GoldenAsset:
        self.auth.check_permission(agent_id, "REVOKE_GOLDEN")
        asset = self.get_golden(golden_id)
        if not asset:
            raise KeyError(f"Golden Asset '{golden_id}' not found.")

        asset.status = GoldenAssetStatus.REVOKED
        asset.metadata["revoke_reason"] = reason
        return self.store.store_golden(asset, allow_update=True)

    def detect_mutation(
        self,
        golden_id: str,
        current_fingerprints: Dict[str, str]
    ) -> Tuple[MutationType, Dict[str, Any]]:
        asset = self.get_golden(golden_id)
        if not asset:
            raise KeyError(f"Golden Asset '{golden_id}' not found.")
        return MutationDetector.detect_mutations(asset, current_fingerprints)
