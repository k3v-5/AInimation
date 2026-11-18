from typing import Dict, List, Optional
from ..core.golden_models import GoldenAsset
from ..core.golden_types import GoldenAssetStatus

class VersionRegistry:
    """Manages version lineage and status transitions across Golden Asset iterations."""
    def __init__(self):
        self._lineage: Dict[str, List[GoldenAsset]] = {} # semantic_id -> list of versions

    def register_version(self, asset: GoldenAsset):
        if asset.semantic_id not in self._lineage:
            self._lineage[asset.semantic_id] = []
        
        # Check if already present
        existing_ids = [a.golden_id for a in self._lineage[asset.semantic_id]]
        if asset.golden_id not in existing_ids:
            self._lineage[asset.semantic_id].append(asset)

    def supersede_version(self, old_asset: GoldenAsset, new_asset: GoldenAsset):
        old_asset.status = GoldenAssetStatus.SUPERSEDED
        new_asset.parent_golden_id = old_asset.golden_id
        new_asset.status = GoldenAssetStatus.ACTIVE
        self.register_version(new_asset)

    def get_versions(self, semantic_id: str) -> List[GoldenAsset]:
        return self._lineage.get(semantic_id, [])

    def get_active_version(self, semantic_id: str) -> Optional[GoldenAsset]:
        versions = self.get_versions(semantic_id)
        for v in reversed(versions):
            if v.status == GoldenAssetStatus.ACTIVE:
                return v
        return None
