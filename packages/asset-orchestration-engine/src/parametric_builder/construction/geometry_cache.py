import hashlib
import json
from typing import Dict, Any, Optional
from ..core.parametric_schema import BuildResult

class GeometryCache:
    def __init__(self):
        self.cache: Dict[str, BuildResult] = {}

    def get(self, fingerprint: str) -> Optional[BuildResult]:
        return self.cache.get(fingerprint)

    def put(self, fingerprint: str, result: BuildResult):
        self.cache[fingerprint] = result

    @staticmethod
    def compute_fingerprint(
        asset_type: str,
        parameters: Dict[str, Any],
        seed: int = 42,
        version: str = "v1.0.0"
    ) -> str:
        payload = {
            "type": asset_type,
            "params": {k: round(v, 3) if isinstance(v, float) else v for k, v in sorted(parameters.items())},
            "seed": seed,
            "ver": version
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
