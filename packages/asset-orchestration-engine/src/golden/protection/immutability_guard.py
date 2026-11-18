from ..core.golden_models import GoldenAsset
from ..core.golden_types import GoldenAssetStatus, GoldenImmutabilityError

class ImmutabilityGuard:
    """Enforces immutability on ACTIVE Golden Assets."""
    
    @staticmethod
    def assert_mutable(asset: GoldenAsset):
        if asset.status == GoldenAssetStatus.ACTIVE:
            raise GoldenImmutabilityError(
                f"Golden Asset '{asset.golden_id}' is ACTIVE and frozen. Direct mutation is prohibited."
            )
