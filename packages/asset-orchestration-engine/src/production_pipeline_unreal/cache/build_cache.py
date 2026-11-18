from typing import Dict, Any, Optional
from ..core.production_schema import ExportManifest

class BuildCache:
    def __init__(self):
        self._cache: Dict[str, ExportManifest] = {}

    def get(self, fingerprint: str) -> Optional[ExportManifest]:
        return self._cache.get(fingerprint)

    def put(self, fingerprint: str, manifest: ExportManifest):
        self._cache[fingerprint] = manifest

    def contains(self, fingerprint: str) -> bool:
        return fingerprint in self._cache

    def clear(self):
        self._cache.clear()
