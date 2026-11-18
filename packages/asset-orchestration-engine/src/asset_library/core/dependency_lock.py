import hashlib
import json
from typing import Dict, Any

class ManifestHasher:
    @staticmethod
    def calculate_manifest_hash(
        template_id: str,
        template_version: str,
        component_versions: Dict[str, str],
        resolved_parameters: Dict[str, Any],
        seed: int = 42
    ) -> str:
        payload = {
            "template_id": template_id,
            "template_version": template_version,
            "components": component_versions,
            "parameters": resolved_parameters,
            "seed": seed
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
