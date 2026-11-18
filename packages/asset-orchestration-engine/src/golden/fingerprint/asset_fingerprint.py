import hashlib
import json
from typing import Dict, Any
from .geometry_fingerprint import GeometryFingerprinter
from .material_fingerprint import MaterialFingerprinter
from .scene_fingerprint import SceneFingerprinter
from .reference_fingerprint import ReferenceFingerprinter

class AssetFingerprinter:
    """Combines modular dimensional fingerprinters to produce a unified cryptographic fingerprint."""
    
    @classmethod
    def compute_all(cls, asset_data: Dict[str, Any]) -> Dict[str, str]:
        geo_data = asset_data.get("geometry", asset_data)
        mat_data = asset_data.get("materials", asset_data)
        scene_data = asset_data.get("scene", asset_data)
        ref_data = asset_data.get("unreal_readiness", asset_data)

        geo_fp = GeometryFingerprinter.compute(geo_data)
        mat_fp = MaterialFingerprinter.compute(mat_data)
        scene_fp = SceneFingerprinter.compute(scene_data)
        ref_fp = ReferenceFingerprinter.compute(ref_data)

        # Master combined fingerprint
        combined = {
            "geometry": geo_fp,
            "materials": mat_fp,
            "scene": scene_fp,
            "reference": ref_fp
        }
        raw = json.dumps(combined, sort_keys=True)
        master_fp = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        return {
            "asset": master_fp,
            "geometry": geo_fp,
            "materials": mat_fp,
            "scene": scene_fp,
            "reference": ref_fp
        }
