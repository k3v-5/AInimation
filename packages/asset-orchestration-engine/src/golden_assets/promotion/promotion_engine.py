import time
from typing import Optional, Dict, Any
from ..core.golden_types import GoldenStatus, VersionBumpType
from ..core.golden_exceptions import GoldenPromotionError
from ..models.golden_asset import GoldenAsset
from ..models.golden_version import GoldenVersion, GoldenVersionInfo
from ..models.golden_baseline import GoldenBaseline
from ..models.reference_asset import ReferenceAsset
from ..validation.golden_validator import GoldenValidator
from ..persistence.golden_store import GoldenAssetStore
from ...evaluation import EvaluationBenchmark

class PromotionEngine:
    """Orchestrates transactional promotion of candidate assets to immutable Golden Assets."""
    def __init__(self, store: GoldenAssetStore):
        self.store = store

    def promote_candidate(
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
        # 1. Validation
        errors = GoldenValidator.validate_for_promotion(benchmark, min_global_score=min_global_score)
        if errors:
            raise GoldenPromotionError(f"Promotion failed validation: {'; '.join(errors)}")

        # 2. Transaction Start
        self.store.begin_transaction()
        try:
            existing = self.store.get_golden_asset(golden_asset_id)
            if existing:
                # Version bump
                parent_v = existing.current_version
                cur_v_obj = GoldenVersion.from_string(parent_v)
                b_type = bump_type or VersionBumpType.MINOR
                new_v_obj = cur_v_obj.bump(b_type)
                new_version = new_v_obj.to_string()
            else:
                parent_v = None
                new_version = "1.0.0"

            # 3. Create Baseline
            baseline_id = f"BASE_{golden_asset_id}_{new_version}".replace(".", "_")
            baseline = GoldenBaseline(
                baseline_id=baseline_id,
                golden_asset_id=golden_asset_id,
                version=new_version,
                metrics=benchmark.metrics,
                dimension_scores={k.value: v.score for k, v in benchmark.dimension_scores.items()},
                global_score=benchmark.weighted_score,
                defects=[d.to_dict() for d in benchmark.defects],
                evaluation_id=benchmark.benchmark_id
            )
            self.store.store_baseline(baseline)

            # 4. Create Version Info
            v_info = GoldenVersionInfo(
                version_str=new_version,
                parent_version=parent_v,
                created_by=approved_by,
                baseline_id=baseline_id,
                evaluation_id=benchmark.benchmark_id,
                status=GoldenStatus.GOLDEN,
                notes=notes
            )

            # 5. Build Golden Asset
            if existing:
                existing.current_version = new_version
                existing.versions[new_version] = v_info
                existing.baselines[new_version] = baseline_id
                existing.status = GoldenStatus.GOLDEN
                existing.approved_at = time.time()
                existing.approved_by = approved_by
                golden_asset = existing
            else:
                golden_asset = GoldenAsset(
                    golden_asset_id=golden_asset_id,
                    semantic_id=semantic_id,
                    asset_family=asset_family,
                    category=category,
                    current_version=new_version,
                    versions={new_version: v_info},
                    baselines={new_version: baseline_id},
                    status=GoldenStatus.GOLDEN,
                    approved_at=time.time(),
                    approved_by=approved_by
                )

            saved = self.store.store_golden_asset(golden_asset, allow_update=True)
            self.store.commit_transaction()
            return saved
        except Exception:
            self.store.rollback_transaction()
            raise
