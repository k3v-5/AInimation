import hashlib
import json
from typing import Dict, Any

class ReferenceFingerprinter:
    """Computes deterministic SHA-256 fingerprints for Unreal Engine readiness and export settings."""
    
    @staticmethod
    def compute(ue_data: Dict[str, Any]) -> str:
        canonical = {
            "axis": ue_data.get("axis", "X_FORWARD_Z_UP"),
            "unit_scale": round(ue_data.get("unit_scale", 1.0), 4),
            "collision": bool(ue_data.get("collision", True)),
            "lods": int(ue_data.get("lods", 3)),
            "nanite": bool(ue_data.get("nanite", False)),
            "material_slots": int(ue_data.get("material_slots", 1)),
            "export_format": ue_data.get("export_format", "FBX")
        }
        raw = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
