from typing import Dict, Any
from ..core.golden_models import GoldenAsset
from ..core.golden_types import GoldenIntegrityError

class IntegrityStore:
    """Validates cryptographic integrity and tracks asset corruption."""
    
    @staticmethod
    def validate_asset_integrity(asset: GoldenAsset):
        if not asset.verify_integrity():
            raise GoldenIntegrityError(f"Golden Asset '{asset.golden_id}' manifest hash mismatch.")

    @staticmethod
    def validate_fingerprints(fingerprints: Dict[str, str]):
        required_keys = {"asset", "geometry", "materials", "scene", "reference"}
        if not required_keys.issubset(set(fingerprints.keys())):
            missing = required_keys - set(fingerprints.keys())
            raise GoldenIntegrityError(f"Incomplete fingerprint. Missing dimensions: {missing}")
