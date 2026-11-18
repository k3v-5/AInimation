from typing import Dict, Any, Tuple
from ..core.golden_models import GoldenAsset
from ..core.golden_types import MutationType

class MutationDetector:
    """Detects mutations and dimensional changes in Golden Assets by comparing cryptographic fingerprints."""
    
    @classmethod
    def detect_mutations(cls, golden_asset: GoldenAsset, current_fingerprints: Dict[str, str]) -> Tuple[MutationType, Dict[str, Any]]:
        stored_fp = golden_asset.fingerprint
        diffs = {}

        for key in ["geometry", "materials", "scene", "reference"]:
            s_val = stored_fp.get(key)
            c_val = current_fingerprints.get(key)
            if s_val != c_val:
                diffs[key] = {"stored": s_val, "current": c_val}

        if not diffs:
            return MutationType.NO_CHANGE, {}

        if len(diffs) > 1:
            return MutationType.MULTIPLE_CHANGES, diffs

        single_key = list(diffs.keys())[0]
        if single_key == "geometry":
            return MutationType.GEOMETRY_CHANGED, diffs
        elif single_key == "materials":
            return MutationType.MATERIAL_CHANGED, diffs
        elif single_key == "scene":
            return MutationType.SCENE_CHANGED, diffs
        elif single_key == "reference":
            return MutationType.REFERENCE_CHANGED, diffs

        return MutationType.CORRUPTED, diffs
