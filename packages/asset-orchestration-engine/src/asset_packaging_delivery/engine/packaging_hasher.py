import hashlib
import json
from typing import Dict, Any

class PackagingHasher:
    @classmethod
    def compute_package_state_hash(
        cls,
        package_id: str,
        asset_id: str,
        content_hash: str,
        delivery_status: str
    ) -> str:
        data = {
            "pkg_id": package_id,
            "asset_id": asset_id,
            "content_hash": content_hash,
            "delivery_status": delivery_status
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
