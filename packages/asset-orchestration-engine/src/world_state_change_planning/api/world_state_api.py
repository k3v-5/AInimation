from typing import Dict, Any, List, Optional
from ..core.world_types import (
    WorldAssetStatus, WorldChangeType, WorldChangeScope, WorldConstraintType,
    ReconciliationState, ContextLevel, TransactionStatus
)
from ..core.world_schema import (
    AssetState, ProjectState, WorldState, ChangeRequest, ChangePlan,
    DryRunResult, SceneSnapshot, TransactionRecord
)
from ..state.world_state_manager import WorldStateManager, WorldDependencyGraph
from ..planning.change_planner import ChangePlanner
from ..transaction.transaction_manager import TransactionManager

class WorldStateAPI:
    """
    World State, Scene Understanding & Change Planning API (AOE v33)
    
    Regla Fundamental:
    LA IA NUNCA ASUME QUÉ EXISTE EN BLENDER NI RECONSTRUYE CIEGAMENTE.
    CONSULTA EL WORLDSTATE, PLANIFICA CAMBIOS MÍNIMOS (Minimal Change Principle),
    VALIDA RESTRICCIONES (ROOF.SHAPE=LOCKED), DETECTA AMBIGÜEDADES Y EJECUTA TRANSACCIONES ATÓMICAS.
    """
    def __init__(self):
        self.state_mgr = WorldStateManager()
        self.tx_mgr = TransactionManager()

    def register_asset(self, asset: AssetState):
        self.state_mgr.register_asset(asset)

    def get_asset_state(self, asset_id: str, level: ContextLevel = ContextLevel.STANDARD) -> Dict[str, Any]:
        return self.state_mgr.get_asset_context(asset_id, level)

    def plan_change(self, request: ChangeRequest) -> ChangePlan:
        return ChangePlanner.plan_change(request, self.state_mgr.state)

    def dry_run_change(self, request: ChangeRequest) -> DryRunResult:
        return ChangePlanner.dry_run(request, self.state_mgr.state)

    def execute_change(self, request: ChangeRequest, current_blender_hash: Optional[str] = None) -> TransactionRecord:
        return self.tx_mgr.execute_transaction(request, self.state_mgr, current_blender_hash)

    def undo(self) -> Optional[TransactionRecord]:
        return self.tx_mgr.undo(self.state_mgr)

    def redo(self) -> Optional[TransactionRecord]:
        return self.tx_mgr.redo(self.state_mgr)
