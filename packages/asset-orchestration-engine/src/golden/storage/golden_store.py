import os
import json
import threading
from typing import Dict, Any, Optional, List
from ..core.golden_models import GoldenAsset
from ..core.golden_types import GoldenAssetStatus, GoldenImmutabilityError, GoldenIntegrityError

class GoldenStore:
    """Thread-safe, verifiable, and transactional persistent storage for Golden Assets."""
    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\GoldenAssets\darx_golden_master_store.json"
        self._lock = threading.RLock()
        self._golden_assets: Dict[str, GoldenAsset] = {}
        self._backup_state: Optional[Dict[str, Any]] = None

        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load_from_disk()

    def store_golden(self, asset: GoldenAsset, allow_update: bool = False) -> GoldenAsset:
        with self._lock:
            existing = self._golden_assets.get(asset.golden_id)
            if existing and existing.status == GoldenAssetStatus.ACTIVE and not allow_update:
                raise GoldenImmutabilityError(
                    f"Golden Asset '{asset.golden_id}' is ACTIVE and immutable. Create a new version."
                )

            asset.manifest_hash = asset.compute_manifest_hash()
            self._golden_assets[asset.golden_id] = asset
            self.save_to_disk()
            return asset

    def get_golden(self, golden_id: str) -> Optional[GoldenAsset]:
        with self._lock:
            asset = self._golden_assets.get(golden_id)
            if asset and not asset.verify_integrity():
                raise GoldenIntegrityError(f"Golden Asset '{golden_id}' corrupted on disk (hash mismatch).")
            return asset

    def list_all(self, semantic_id: Optional[str] = None) -> List[GoldenAsset]:
        with self._lock:
            assets = list(self._golden_assets.values())
            if semantic_id:
                assets = [a for a in assets if a.semantic_id == semantic_id]
            return assets

    # Transactional methods
    def begin_transaction(self):
        with self._lock:
            self._backup_state = {k: v.to_dict() for k, v in self._golden_assets.items()}

    def commit_transaction(self):
        with self._lock:
            self._backup_state = None
            self.save_to_disk()

    def rollback_transaction(self):
        with self._lock:
            if self._backup_state is not None:
                self._golden_assets = {k: GoldenAsset.from_dict(v) for k, v in self._backup_state.items()}
                self._backup_state = None
                self.save_to_disk()

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            payload = {k: v.to_dict() for k, v in self._golden_assets.items()}
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

    def load_from_disk(self):
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        if os.path.getsize(self.persistence_path) == 0:
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._golden_assets = {}
                    for k, v in data.items():
                        asset = GoldenAsset.from_dict(v)
                        if not asset.verify_integrity():
                            raise GoldenIntegrityError(f"Golden Asset '{k}' corrupted on disk.")
                        self._golden_assets[k] = asset
            except GoldenIntegrityError:
                raise
            except Exception as e:
                print(f"[GoldenStore] Warning loading disk store: {e}")
