import hashlib
import json
from typing import Dict, Any, List, Tuple
from ..core.asset_schema import LibraryAssetRecord

class FingerprintMatcher:
    @staticmethod
    def compute_geometry_fingerprint(dimensions: Dict[str, float], polycount: int, vertex_layout: str = "standard") -> str:
        payload = {
            "dims": {k: round(v, 2) for k, v in sorted(dimensions.items())},
            "poly": polycount,
            "layout": vertex_layout
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def find_duplicates(assets: List[LibraryAssetRecord]) -> List[Tuple[str, str]]:
        """Devuelve pares (asset_id_A, asset_id_B) que comparten fingerprint idéntico."""
        seen: Dict[str, str] = {}
        duplicates = []
        for a in assets:
            if a.geometry_fingerprint in seen:
                duplicates.append((seen[a.geometry_fingerprint], a.asset_id))
            else:
                seen[a.geometry_fingerprint] = a.asset_id
        return duplicates
