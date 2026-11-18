from typing import Dict, List, Optional
from .asset_schema import LibraryAssetRecord
from .asset_status import AssetState

class AssetRegistry:
    def __init__(self):
        self.assets: Dict[str, LibraryAssetRecord] = {}

    def register_asset(self, asset: LibraryAssetRecord):
        self.assets[asset.asset_id] = asset

    def get_asset(self, asset_id: str) -> Optional[LibraryAssetRecord]:
        return self.assets.get(asset_id)

    def list_all(self) -> List[LibraryAssetRecord]:
        return list(self.assets.values())

    def record_failure(self, asset_id: str):
        asset = self.assets.get(asset_id)
        if asset:
            asset.failure_count += 1
            if asset.failure_count >= 5:
                asset.state = AssetState.QUARANTINED

    def record_success(self, asset_id: str):
        asset = self.assets.get(asset_id)
        if asset:
            asset.success_count += 1

    def lock_asset(self, asset_id: str):
        asset = self.assets.get(asset_id)
        if asset:
            asset.state = AssetState.PRODUCTION_LOCKED
