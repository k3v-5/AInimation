import copy
import time
from typing import Dict, Any, List, Optional
from ..core.world_types import ContextLevel, WorldAssetStatus
from ..core.world_schema import WorldState, AssetState, SceneSnapshot, ComponentMetadata

class WorldStateManager:
    def __init__(self):
        self.state = WorldState()
        self.components: Dict[str, ComponentMetadata] = {}

    def register_asset(self, asset: AssetState):
        self.state.assets[asset.asset_id] = copy.deepcopy(asset)

    def get_asset(self, asset_id: str) -> Optional[AssetState]:
        return self.state.assets.get(asset_id)

    def get_asset_context(self, asset_id: str, level: ContextLevel = ContextLevel.STANDARD) -> Dict[str, Any]:
        asset = self.get_asset(asset_id)
        if not asset:
            return {"error": f"Asset {asset_id} not found in WorldState."}

        if level == ContextLevel.MINIMAL:
            return {"id": asset.asset_id, "type": asset.asset_type, "status": asset.status.value, "version": asset.version}
        elif level == ContextLevel.STANDARD:
            return {
                "id": asset.asset_id,
                "type": asset.asset_type,
                "size": f"{asset.bounds['w']}x{asset.bounds['d']}x{asset.bounds['h']}m",
                "components": len(asset.components),
                "status": asset.status.value,
                "version": asset.version,
                "parameters": asset.parameters,
                "dirty": asset.status == WorldAssetStatus.DIRTY
            }
        else: # DETAILED & DEBUG
            return {
                "id": asset.asset_id,
                "type": asset.asset_type,
                "status": asset.status.value,
                "version": asset.version,
                "bounds": asset.bounds,
                "parameters": asset.parameters,
                "components": asset.components,
                "geometry_hash": asset.geometry_hash,
                "locked_properties": asset.locked_properties
            }

    def create_snapshot(self) -> SceneSnapshot:
        snap_id = f"SNAP_{int(time.time()*1000)}"
        return SceneSnapshot(
            snapshot_id=snap_id,
            assets_state=copy.deepcopy(self.state.assets)
        )

    def restore_snapshot(self, snapshot: SceneSnapshot):
        self.state.assets = copy.deepcopy(snapshot.assets_state)

class WorldDependencyGraph:
    DEPENDENCY_MAP = {
        "door.width": {
            "affected": ["DOOR", "DOOR_FRAME", "WALL_OPENING", "COLLISION"],
            "unaffected": ["ROOF", "WINDOWS", "STAIRS", "FOUNDATION"]
        },
        "roof.pitch": {
            "affected": ["ROOF", "ROOF_SUPPORT", "ROOF_COLLISION", "ROOF_NAVIGATION"],
            "unaffected": ["DOOR", "WINDOWS", "FLOOR", "FOUNDATION"]
        },
        "roof.shape": {
            "affected": ["ROOF", "ROOF_SUPPORT", "ROOF_COLLISION"],
            "unaffected": ["DOOR", "WINDOWS", "FLOOR", "STAIRS", "FOUNDATION"]
        },
        "windows.count": {
            "affected": ["WINDOWS", "WALL_OPENINGS", "VISUAL_VALIDATION"],
            "unaffected": ["DOOR", "STAIRS", "ROOF", "FOUNDATION", "COLLISION"]
        }
    }

    @classmethod
    def get_impact(cls, property_path: str) -> Dict[str, List[str]]:
        clean_prop = property_path.lower()
        if clean_prop in cls.DEPENDENCY_MAP:
            return cls.DEPENDENCY_MAP[clean_prop]
        return {
            "affected": [property_path.upper()],
            "unaffected": ["OTHER_COMPONENTS"]
        }
