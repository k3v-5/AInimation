import hashlib
import json
from typing import Dict, Any

class SceneFingerprinter:
    """Computes deterministic SHA-256 fingerprints for scene hierarchy and collections."""
    
    @staticmethod
    def compute(scene_data: Dict[str, Any]) -> str:
        canonical = {
            "collection_names": sorted(scene_data.get("collection_names", [])),
            "hierarchy": scene_data.get("hierarchy", {}),
            "transforms": scene_data.get("transforms", {}),
            "pivot": scene_data.get("pivot", [0.0, 0.0, 0.0])
        }
        raw = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
