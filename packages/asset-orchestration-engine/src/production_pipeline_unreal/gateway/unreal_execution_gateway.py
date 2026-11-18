import time
from typing import Dict, Any, List, Optional
from ..core.production_types import (
    AssetLifecycle, QualityGateStatus, SourceOwnership
)
from ..core.production_schema import (
    ProductionAsset, ExportManifest, PublicationRecord, QualityGateReport
)
from ..contracts.naming_path_policy import NamingPathPolicy

class UnrealExecutionGateway:
    def __init__(self):
        self.staged_assets: Dict[str, ProductionAsset] = {}
        self.published_assets: Dict[str, ProductionAsset] = {}
        self.publication_history: List[PublicationRecord] = []

    def import_to_staging(
        self,
        manifest: ExportManifest,
        ownership: SourceOwnership = SourceOwnership.AI
    ) -> ProductionAsset:
        staging_path = NamingPathPolicy.get_staging_path(manifest.asset_id)
        asset = ProductionAsset(
            asset_id=manifest.asset_id,
            version=manifest.version,
            status=AssetLifecycle.STAGING,
            unreal_path=staging_path,
            manifest=manifest,
            ownership=ownership,
            is_manual_modified=False
        )
        self.staged_assets[manifest.asset_id] = asset
        return asset

    def mark_manual_modified_in_unreal(self, asset_id: str):
        if asset_id in self.published_assets:
            self.published_assets[asset_id].is_manual_modified = True
            self.published_assets[asset_id].ownership = SourceOwnership.HYBRID

    def publish_asset(
        self,
        asset_id: str,
        category: str = "Environment",
        simulate_failure: bool = False
    ) -> PublicationRecord:
        if asset_id not in self.staged_assets:
            raise KeyError(f"Asset '{asset_id}' is not staged.")

        staged = self.staged_assets[asset_id]

        # Comprobar protección de modificación manual
        if asset_id in self.published_assets and self.published_assets[asset_id].is_manual_modified:
            raise PermissionError(f"MANUAL_MODIFICATION_PROTECTED: Asset '{asset_id}' was manually modified in Unreal. Silent overwrite blocked.")

        prev_version = self.published_assets[asset_id].version if asset_id in self.published_assets else None
        target_path = NamingPathPolicy.get_published_path(category, asset_id)

        pub_id = f"PUB_{int(time.time()*1000)}"

        if simulate_failure:
            # Fallo simulado -> Rollback automático
            rec_fail = PublicationRecord(
                publication_id=pub_id,
                asset_id=asset_id,
                version=staged.version,
                target_path=target_path,
                previous_version=prev_version,
                status="ROLLED_BACK"
            )
            return rec_fail

        staged.status = AssetLifecycle.PUBLISHED
        staged.unreal_path = target_path
        self.published_assets[asset_id] = staged
        
        rec = PublicationRecord(
            publication_id=pub_id,
            asset_id=asset_id,
            version=staged.version,
            target_path=target_path,
            previous_version=prev_version,
            status="COMMITTED"
        )
        return rec
