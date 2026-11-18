from typing import Dict, Any, Optional, List, Tuple
from ..core.game_ready_engine import GameReadyEngine
from ..transforms.pivot_manager import PivotType
from ..lod.lod_profile import GameReadyLODProfile
from ..collision.collision_profile import CollisionProfile

class GameReadyAPI:
    def __init__(self, game_ready_engine: GameReadyEngine):
        self.engine = game_ready_engine

    def prepare_asset_for_unreal(
        self,
        asset_id: str,
        category: str = "Weapons",
        geometry_status: str = "APPROVED",
        appearance_status: str = "APPROVED",
        pivot_type: str = "BOTTOM_CENTER",
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        return self.engine.process_game_ready(
            asset_id=asset_id,
            category=category,
            geometry_status=geometry_status,
            appearance_status=appearance_status,
            pivot_type=PivotType(pivot_type),
            scope=scope,
            dry_run=dry_run
        )

    def add_socket(self, socket_id: str, parent_component: str, location: Tuple[float, float, float] = (0,0,0)) -> Dict[str, Any]:
        return self.engine.add_socket(socket_id, parent_component, location)

    def get_manifest(self, asset_id: str) -> Optional[Any]:
        return self.engine.get_manifest(asset_id)
