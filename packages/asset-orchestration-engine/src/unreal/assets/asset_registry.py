from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class UnrealAssetReference:
    logical_asset_id: str
    unreal_package_path: str
    asset_class: str = "StaticMesh" # StaticMesh, Blueprint, Material
    version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)

class UnrealAssetRegistry:
    def __init__(self):
        self.assets: Dict[str, UnrealAssetReference] = {} # logical_id -> reference

    def register_asset(self, asset: UnrealAssetReference):
        self.assets[asset.logical_asset_id] = asset

    def get_asset(self, logical_asset_id: str) -> Optional[UnrealAssetReference]:
        return self.assets.get(logical_asset_id)

    def resolve_path(self, logical_asset_id: str) -> Optional[str]:
        asset = self.get_asset(logical_asset_id)
        return asset.unreal_package_path if asset else None

    def list_assets(self) -> List[UnrealAssetReference]:
        return list(self.assets.values())
