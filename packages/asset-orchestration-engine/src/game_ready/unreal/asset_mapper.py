from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class UnrealAssetMapping:
    source_asset_id: str
    fbx_filename: str
    unreal_asset_name: str
    unreal_package_path: str
    material_paths: Dict[str, str]

class AssetMapper:
    @staticmethod
    def create_mapping(asset_id: str, category: str = "Weapons") -> UnrealAssetMapping:
        # Formatear nombre en PascalCase con prefijo SM_
        clean_name = "".join(w.capitalize() for w in asset_id.replace("-", "_").split("_"))
        if not clean_name.startswith("SM_"):
            clean_name = f"SM_{clean_name}"

        return UnrealAssetMapping(
            source_asset_id=asset_id,
            fbx_filename=f"{clean_name}.fbx",
            unreal_asset_name=clean_name,
            unreal_package_path=f"/Game/Assets/{category}/{clean_name}/{clean_name}",
            material_paths={}
        )
