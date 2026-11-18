from typing import Dict, List, Optional
from ..models.golden_asset import GoldenAsset
from ..models.reference_asset import ReferenceAsset
from ..models.golden_baseline import GoldenBaseline
from ..core.golden_exceptions import GoldenDuplicateError

class GoldenAssetRegistry:
    """In-memory registry managing Golden Assets with uniqueness and lookup guarantees."""
    def __init__(self):
        self._assets: Dict[str, GoldenAsset] = {}
        self._semantic_index: Dict[str, str] = {}

    def register(self, asset: GoldenAsset, allow_overwrite: bool = False):
        if not allow_overwrite:
            if asset.golden_asset_id in self._assets:
                raise GoldenDuplicateError(f"Golden Asset ID '{asset.golden_asset_id}' is already registered.")
            if asset.semantic_id in self._semantic_index and self._semantic_index[asset.semantic_id] != asset.golden_asset_id:
                raise GoldenDuplicateError(f"Semantic ID '{asset.semantic_id}' is already assigned to golden asset '{self._semantic_index[asset.semantic_id]}'.")

        self._assets[asset.golden_asset_id] = asset
        self._semantic_index[asset.semantic_id] = asset.golden_asset_id

    def get(self, golden_asset_id: str) -> Optional[GoldenAsset]:
        return self._assets.get(golden_asset_id)

    def get_by_semantic_id(self, semantic_id: str) -> Optional[GoldenAsset]:
        g_id = self._semantic_index.get(semantic_id)
        return self._assets.get(g_id) if g_id else None

    def list_all(self) -> List[GoldenAsset]:
        return list(self._assets.values())

class ReferenceRegistry:
    """Registry managing Reference Assets."""
    def __init__(self):
        self._references: Dict[str, ReferenceAsset] = {}

    def register(self, ref: ReferenceAsset):
        self._references[ref.reference_id] = ref

    def get(self, reference_id: str) -> Optional[ReferenceAsset]:
        return self._references.get(reference_id)

    def list_all(self) -> List[ReferenceAsset]:
        return list(self._references.values())

class BaselineRegistry:
    """Registry managing Golden Baselines."""
    def __init__(self):
        self._baselines: Dict[str, GoldenBaseline] = {}

    def register(self, baseline: GoldenBaseline):
        self._baselines[baseline.baseline_id] = baseline

    def get(self, baseline_id: str) -> Optional[GoldenBaseline]:
        return self._baselines.get(baseline_id)

    def list_for_golden_asset(self, golden_asset_id: str) -> List[GoldenBaseline]:
        return [b for b in self._baselines.values() if b.golden_asset_id == golden_asset_id]
