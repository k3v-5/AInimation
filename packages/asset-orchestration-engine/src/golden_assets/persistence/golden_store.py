import os
import json
import threading
from typing import Dict, Any, Optional, List
from ..models.golden_asset import GoldenAsset
from ..models.reference_asset import ReferenceAsset
from ..models.golden_baseline import GoldenBaseline
from ..core.golden_exceptions import GoldenIntegrityError, GoldenImmutableError
from ..core.golden_types import GoldenStatus

class GoldenAssetStore:
    """Thread-safe and verifiable persistent storage for Golden Assets, Baselines, and References."""
    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\GoldenAssets\darx_golden_assets.json"
        self._lock = threading.RLock()
        self._golden_assets: Dict[str, GoldenAsset] = {}
        self._references: Dict[str, ReferenceAsset] = {}
        self._baselines: Dict[str, GoldenBaseline] = {}
        self._uncommitted_backup: Optional[Dict[str, Any]] = None

        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load_from_disk()

    def store_golden_asset(self, asset: GoldenAsset, allow_update: bool = False) -> GoldenAsset:
        with self._lock:
            existing = self._golden_assets.get(asset.golden_asset_id)
            if existing and existing.status == GoldenStatus.GOLDEN and not allow_update:
                raise GoldenImmutableError(f"Golden Asset '{asset.golden_asset_id}' is published and immutable. Create a new version.")

            asset.compute_hashes()
            self._golden_assets[asset.golden_asset_id] = asset
            self.save_to_disk()
            return asset

    def store_reference_asset(self, ref: ReferenceAsset) -> ReferenceAsset:
        with self._lock:
            ref.content_hash = ref.compute_hash()
            self._references[ref.reference_id] = ref
            self.save_to_disk()
            return ref

    def store_baseline(self, baseline: GoldenBaseline) -> GoldenBaseline:
        with self._lock:
            baseline.content_hash = baseline.compute_hash()
            self._baselines[baseline.baseline_id] = baseline
            self.save_to_disk()
            return baseline

    def get_golden_asset(self, golden_asset_id: str) -> Optional[GoldenAsset]:
        with self._lock:
            asset = self._golden_assets.get(golden_asset_id)
            if asset and not asset.verify_integrity():
                raise GoldenIntegrityError(f"Golden Asset '{golden_asset_id}' failed cryptographic integrity check.")
            return asset

    def get_reference_asset(self, reference_id: str) -> Optional[ReferenceAsset]:
        with self._lock:
            return self._references.get(reference_id)

    def get_baseline(self, baseline_id: str) -> Optional[GoldenBaseline]:
        with self._lock:
            b = self._baselines.get(baseline_id)
            if b and not b.verify_integrity():
                raise GoldenIntegrityError(f"Baseline '{baseline_id}' failed cryptographic integrity check.")
            return b

    def list_golden_assets(self) -> List[GoldenAsset]:
        with self._lock:
            return list(self._golden_assets.values())

    def list_reference_assets(self) -> List[ReferenceAsset]:
        with self._lock:
            return list(self._references.values())

    def list_baselines(self) -> List[GoldenBaseline]:
        with self._lock:
            return list(self._baselines.values())

    # Transaction support for crash recovery
    def begin_transaction(self):
        with self._lock:
            self._uncommitted_backup = {
                "golden_assets": {k: v.to_dict() for k, v in self._golden_assets.items()},
                "references": {k: v.to_dict() for k, v in self._references.items()},
                "baselines": {k: v.to_dict() for k, v in self._baselines.items()}
            }

    def commit_transaction(self):
        with self._lock:
            self._uncommitted_backup = None
            self.save_to_disk()

    def rollback_transaction(self):
        with self._lock:
            if self._uncommitted_backup:
                self._golden_assets = {k: GoldenAsset.from_dict(v) for k, v in self._uncommitted_backup["golden_assets"].items()}
                self._references = {k: ReferenceAsset.from_dict(v) for k, v in self._uncommitted_backup["references"].items()}
                self._baselines = {k: GoldenBaseline.from_dict(v) for k, v in self._uncommitted_backup["baselines"].items()}
                self._uncommitted_backup = None
                self.save_to_disk()

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            payload = {
                "golden_assets": {k: v.to_dict() for k, v in self._golden_assets.items()},
                "references": {k: v.to_dict() for k, v in self._references.items()},
                "baselines": {k: v.to_dict() for k, v in self._baselines.items()}
            }
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
                    for k, v in data.get("golden_assets", {}).items():
                        asset = GoldenAsset.from_dict(v)
                        if not asset.verify_integrity():
                            raise GoldenIntegrityError(f"Golden Asset '{k}' corrupted on disk.")
                        self._golden_assets[k] = asset

                    self._references = {k: ReferenceAsset.from_dict(v) for k, v in data.get("references", {}).items()}
                    
                    self._baselines = {}
                    for k, v in data.get("baselines", {}).items():
                        b = GoldenBaseline.from_dict(v)
                        if not b.verify_integrity():
                            raise GoldenIntegrityError(f"Baseline '{k}' corrupted on disk.")
                        self._baselines[k] = b
            except GoldenIntegrityError:
                raise
            except Exception as e:
                print(f"[GoldenAssetStore] Warning loading disk store: {e}")
