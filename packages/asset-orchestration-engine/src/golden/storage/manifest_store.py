import json
import hashlib
from typing import Dict, Any
from ..core.golden_models import GoldenAsset
from ..core.golden_types import GoldenIntegrityError

class ManifestStore:
    """Handles serialization, cryptographic signing, and verification of Golden Asset manifests."""
    
    @staticmethod
    def generate_manifest(asset: GoldenAsset) -> Dict[str, Any]:
        manifest = {
            "golden_id": asset.golden_id,
            "semantic_id": asset.semantic_id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "version": asset.version,
            "fingerprint": asset.fingerprint,
            "evaluation": {
                "evaluation_id": asset.evaluation_id,
                "score": round(asset.baseline_score, 4),
                "minimum_acceptable_score": round(asset.minimum_acceptable_score, 4)
            },
            "status": asset.status.value,
            "parent_golden_id": asset.parent_golden_id,
            "integrity": {
                "manifest_hash": asset.manifest_hash
            }
        }
        return manifest

    @staticmethod
    def verify_manifest(manifest_data: Dict[str, Any]) -> bool:
        integrity = manifest_data.get("integrity", {})
        stored_hash = integrity.get("manifest_hash", "")
        if not stored_hash:
            return False

        # Reconstruct canonical data
        data = {
            "golden_id": manifest_data["golden_id"],
            "semantic_id": manifest_data["semantic_id"],
            "asset_name": manifest_data.get("asset_name", ""),
            "asset_type": manifest_data.get("asset_type", "weapon"),
            "version": manifest_data.get("version", 1),
            "source_asset_id": manifest_data.get("source_asset_id"),
            "fingerprint": {k: manifest_data["fingerprint"][k] for k in sorted(manifest_data.get("fingerprint", {}).keys())},
            "baseline_score": round(manifest_data.get("evaluation", {}).get("score", 0.0), 4),
            "minimum_acceptable_score": round(manifest_data.get("evaluation", {}).get("minimum_acceptable_score", 0.85), 4),
            "parent_golden_id": manifest_data.get("parent_golden_id")
        }
        computed = hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        return computed == stored_hash
