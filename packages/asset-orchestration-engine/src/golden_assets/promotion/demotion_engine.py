import time
from typing import Optional
from ..core.golden_types import GoldenStatus
from ..core.golden_exceptions import GoldenAssetException
from ..models.golden_asset import GoldenAsset
from ..persistence.golden_store import GoldenAssetStore

class DemotionEngine:
    """Manages deprecation, archiving, and revocation of Golden Assets while preserving full history."""
    def __init__(self, store: GoldenAssetStore):
        self.store = store

    def demote_golden(
        self,
        golden_asset_id: str,
        target_status: GoldenStatus,
        reason: str,
        actor: str = "agent.strategy",
        successor_id: Optional[str] = None
    ) -> GoldenAsset:
        asset = self.store.get_golden_asset(golden_asset_id)
        if not asset:
            raise KeyError(f"Golden Asset '{golden_asset_id}' not found.")

        if target_status not in (GoldenStatus.DEPRECATED, GoldenStatus.ARCHIVED, GoldenStatus.REVOKED):
            raise GoldenAssetException(f"Invalid demotion target status: {target_status}")

        asset.status = target_status
        asset.successor_id = successor_id
        asset.metadata["demoted_at"] = time.time()
        asset.metadata["demoted_by"] = actor
        asset.metadata["demotion_reason"] = reason

        return self.store.store_golden_asset(asset, allow_update=True)
