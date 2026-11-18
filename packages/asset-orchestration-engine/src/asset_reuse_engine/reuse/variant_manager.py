import hashlib
import json
import uuid
from typing import Dict, Any, Optional, List
from ..core.asset_schema import AssetVariant

class VariantManager:
    def __init__(self):
        self.variants_by_hash: Dict[str, AssetVariant] = {}
        self.variants_by_parent: Dict[str, List[AssetVariant]] = {}

    def create_or_get_variant(
        self,
        parent_asset_id: str,
        overrides: Dict[str, Any]
    ) -> AssetVariant:
        vhash = self.compute_variant_hash(parent_asset_id, overrides)
        if vhash in self.variants_by_hash:
            return self.variants_by_hash[vhash]

        var_id = f"{parent_asset_id}_var_{uuid.uuid4().hex[:4]}"
        variant = AssetVariant(
            variant_id=var_id,
            parent_asset_id=parent_asset_id,
            parameter_overrides=overrides,
            variant_hash=vhash
        )
        self.variants_by_hash[vhash] = variant
        if parent_asset_id not in self.variants_by_parent:
            self.variants_by_parent[parent_asset_id] = []
        self.variants_by_parent[parent_asset_id].append(variant)
        return variant

    @staticmethod
    def compute_variant_hash(parent_id: str, overrides: Dict[str, Any]) -> str:
        payload = {"parent": parent_id, "params": {k: round(v, 2) if isinstance(v, float) else v for k, v in sorted(overrides.items())}}
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

class InstancingEngine:
    @staticmethod
    def create_instances(canonical_asset_id: str, count: int) -> Dict[str, Any]:
        """
        Crea 1 referencia canónica + (count - 1) instancias ligeras con transform overrides.
        """
        instances = []
        for i in range(1, count):
            instances.append({
                "instance_id": f"{canonical_asset_id}_inst_{i:03d}",
                "source_canonical_id": canonical_asset_id,
                "is_instance": True
            })
        return {
            "canonical_asset_id": canonical_asset_id,
            "total_count": count,
            "canonical_count": 1,
            "instances_count": count - 1,
            "instances": instances
        }
