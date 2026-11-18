from typing import Dict, Any, Optional
from ..core.world_types import ReconciliationState
from ..core.world_schema import AssetState

class ReconciliationEngine:
    @staticmethod
    def detect_external_modifications(asset: AssetState, current_blender_geo_hash: Optional[str] = None) -> ReconciliationState:
        if current_blender_geo_hash is None or not asset.geometry_hash:
            return ReconciliationState.IDENTICAL

        if current_blender_geo_hash != asset.geometry_hash:
            return ReconciliationState.CONFLICT
        return ReconciliationState.IDENTICAL

    @classmethod
    def verify_reconciliation(cls, asset: AssetState, current_blender_geo_hash: Optional[str] = None):
        state = cls.detect_external_modifications(asset, current_blender_geo_hash)
        if state == ReconciliationState.CONFLICT:
            raise ValueError(f"EXTERNAL_MODIFICATION: Asset '{asset.asset_id}' was modified externally in Blender (Stored: {asset.geometry_hash}, Actual: {current_blender_geo_hash}).")
