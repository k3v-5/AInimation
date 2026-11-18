import copy
import time
from typing import Dict, Any, List, Optional
from ..core.world_types import TransactionStatus, WorldAssetStatus
from ..core.world_schema import (
    ChangeRequest, ChangePlan, TransactionRecord, SceneSnapshot, AssetState
)
from ..state.world_state_manager import WorldStateManager
from ..planning.change_planner import ChangePlanner
from .reconciliation_engine import ReconciliationEngine

class TransactionManager:
    """
    Transaction Manager (AOE v33):
    Garantiza atomicidad, snapshots pre/post mutación, detección de ejecuciones duplicadas (ALREADY_APPLIED),
    rollback y capacidades de Undo/Redo.
    """
    def __init__(self):
        self.history: List[TransactionRecord] = []
        self.undo_stack: List[TransactionRecord] = []
        self.applied_plan_hashes: set = set()

    def execute_transaction(
        self,
        request: ChangeRequest,
        state_mgr: WorldStateManager,
        current_blender_hash: Optional[str] = None
    ) -> TransactionRecord:
        # 1. Crear Plan
        plan = ChangePlanner.plan_change(request, state_mgr.state)

        # 2. Comprobar si ya fue aplicado (Idempotencia)
        if plan.plan_hash in self.applied_plan_hashes:
            raise ValueError(f"ALREADY_APPLIED: Change plan '{plan.plan_id}' with hash '{plan.plan_hash}' was already applied.")

        target_asset = state_mgr.get_asset(plan.target_asset_id)
        if not target_asset:
            raise ValueError(f"Asset '{plan.target_asset_id}' not found.")

        # 3. Comprobar modificaciones externas en Blender
        ReconciliationEngine.verify_reconciliation(target_asset, current_blender_hash)

        # 4. Snapshot Pre-Estado
        pre_snap = state_mgr.create_snapshot()
        tx_id = f"TX_{int(time.time()*1000)}"
        record = TransactionRecord(
            transaction_id=tx_id,
            request=request,
            plan=plan,
            pre_state=pre_snap,
            status=TransactionStatus.BEGIN
        )

        try:
            # 5. Aplicar Mutación de Estado
            target_asset.parameters[request.property_path] = request.new_value
            target_asset.version += 1
            target_asset.status = WorldAssetStatus.VALID

            # 6. Snapshot Post-Estado y Commit
            post_snap = state_mgr.create_snapshot()
            record.post_state = post_snap
            record.status = TransactionStatus.COMMITTED

            self.applied_plan_hashes.add(plan.plan_hash)
            self.history.append(record)
            return record

        except Exception as e:
            # 7. Rollback automático ante fallo
            state_mgr.restore_snapshot(pre_snap)
            record.status = TransactionStatus.ROLLED_BACK
            raise e

    def undo(self, state_mgr: WorldStateManager) -> Optional[TransactionRecord]:
        if not self.history:
            return None
        last_tx = self.history.pop()
        state_mgr.restore_snapshot(last_tx.pre_state)
        self.undo_stack.append(last_tx)
        if last_tx.plan.plan_hash in self.applied_plan_hashes:
            self.applied_plan_hashes.remove(last_tx.plan.plan_hash)
        return last_tx

    def redo(self, state_mgr: WorldStateManager) -> Optional[TransactionRecord]:
        if not self.undo_stack:
            return None
        tx_to_redo = self.undo_stack.pop()
        state_mgr.restore_snapshot(tx_to_redo.post_state) # type: ignore
        self.history.append(tx_to_redo)
        self.applied_plan_hashes.add(tx_to_redo.plan.plan_hash)
        return tx_to_redo
