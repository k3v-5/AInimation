from typing import Dict, List, Optional
from ..core.golden_models import GoldenAsset
from ..core.golden_types import GoldenAssetStatus, GoldenDuplicateError

class GoldenRegistry:
    """Registry managing Golden Assets with duplicate checks and semantic lookups."""
    def __init__(self):
        self._assets: Dict[str, GoldenAsset] = {}
        self._active_by_semantic: Dict[str, str] = {}

    def register(self, asset: GoldenAsset, allow_update: bool = False):
        if not allow_update and asset.golden_id in self._assets:
            raise GoldenDuplicateError(f"Golden Asset ID '{asset.golden_id}' is already registered.")

        self._assets[asset.golden_id] = asset
        if asset.status == GoldenAssetStatus.ACTIVE:
            self._active_by_semantic[asset.semantic_id] = asset.golden_id

    def get(self, golden_id: str) -> Optional[GoldenAsset]:
        return self._assets.get(golden_id)

    def get_active(self, semantic_id: str) -> Optional[GoldenAsset]:
        g_id = self._active_by_semantic.get(semantic_id)
        return self._assets.get(g_id) if g_id else None

    def list_all(self) -> List[GoldenAsset]:
        return list(self._assets.values())
