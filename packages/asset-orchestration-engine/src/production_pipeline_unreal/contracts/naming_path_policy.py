from typing import Dict, Any

class NamingPathPolicy:
    PREFIXES: Dict[str, str] = {
        "STATIC_MESH": "SM_",
        "MATERIAL": "M_",
        "MATERIAL_INSTANCE": "MI_",
        "TEXTURE": "TX_",
        "COLLISION": "UCX_",
        "BLUEPRINT": "BP_",
        "DATA_ASSET": "DA_"
    }

    @classmethod
    def get_mesh_name(cls, asset_name: str) -> str:
        return f"{cls.PREFIXES['STATIC_MESH']}{asset_name}"

    @classmethod
    def get_material_instance_name(cls, asset_name: str) -> str:
        return f"{cls.PREFIXES['MATERIAL_INSTANCE']}{asset_name}"

    @classmethod
    def get_collision_name(cls, asset_name: str) -> str:
        return f"{cls.PREFIXES['COLLISION']}{asset_name}"

    @classmethod
    def get_data_asset_name(cls, asset_name: str) -> str:
        return f"{cls.PREFIXES['DATA_ASSET']}{asset_name}"

    @classmethod
    def get_staging_path(cls, asset_name: str) -> str:
        return f"/Game/_Staging/{asset_name}/"

    @classmethod
    def get_published_path(cls, category: str, asset_name: str) -> str:
        return f"/Game/Published/{category}/{asset_name}/"
