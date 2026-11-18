import hashlib
import json
from typing import Dict, Any

class MaterialFingerprinter:
    """Computes deterministic SHA-256 fingerprints for PBR materials and shader setups."""
    
    @staticmethod
    def compute(material_data: Any) -> str:
        if isinstance(material_data, list):
            mat_dict = {"material_names": material_data}
        elif isinstance(material_data, dict):
            mat_dict = material_data
        else:
            mat_dict = {}

        canonical = {
            "material_names": sorted(mat_dict.get("material_names", [])),
            "shader_type": mat_dict.get("shader_type", "PrincipledBSDF"),
            "base_color": mat_dict.get("base_color", [0.8, 0.8, 0.8, 1.0]),
            "metallic": round(mat_dict.get("metallic", 0.0), 4),
            "roughness": round(mat_dict.get("roughness", 0.5), 4),
            "emissive": round(mat_dict.get("emissive", 0.0), 4),
            "textures": sorted(mat_dict.get("textures", [])),
            "assignments": mat_dict.get("assignments", {})
        }
        raw = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
