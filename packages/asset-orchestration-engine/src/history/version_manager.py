from typing import Dict

class VersionManager:
    def __init__(self):
        self.asset_versions: Dict[str, int] = {}

    def get_version(self, asset_id: str) -> int:
        return self.asset_versions.get(asset_id, 1)

    def increment_version(self, asset_id: str) -> int:
        cur = self.asset_versions.get(asset_id, 1)
        self.asset_versions[asset_id] = cur + 1
        return cur + 1
