from typing import Dict, Any

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
