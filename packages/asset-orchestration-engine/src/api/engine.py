from typing import Dict, Any, Optional, Union
from ..core.state_manager import StateManager
from ..core.asset_manager import AssetManager
from ..planning.planner import Planner, ChangeBudget
from ..planning.change_analyzer import ChangeAnalyzer
from ..planning.plan_generator import PlanGenerator
from ..planning.scope_manager import ScopeSpec
from ..execution.transaction_manager import TransactionManager
from ..execution.rollback_manager import RollbackManager
from ..execution.executor import PlanExecutor
from ..blender.blender_adapter import BlenderAdapter
from ..validation.validator import QualityGateValidator
from ..history.snapshot_manager import SnapshotManager
from ..history.version_manager import VersionManager
from ..history.operation_log import OperationLog
from .asset_api import AssetAPI
from .inspection_api import InspectionAPI
from .modification_api import ModificationAPI
from .validation_api import ValidationAPI
from .plan_api import PlanAPI

class AssetOrchestrationEngine:
    """
    Asset Orchestration Engine v2 (AOE v2)
    
    Principios Invariables:
    1. The engine must prefer deterministic state modification over generative reconstruction.
    2. Never rebuild an existing asset when the requested change can be achieved by modifying an existing component or parameter.
    3. When the engine cannot determine the intended target unambiguously, it must stop rather than guess.
    """
    def __init__(self, blender_adapter: Optional[BlenderAdapter] = None):
        # 1. Core & State
        self.state_manager = StateManager()
        self.asset_manager = AssetManager(self.state_manager)

        # 2. Planning & Execution
        self.change_analyzer = ChangeAnalyzer()
        self.planner = Planner(self.change_analyzer)
        self.plan_generator = PlanGenerator(self.change_analyzer)
        self.tx_manager = TransactionManager()
        self.rollback_mgr = RollbackManager()
        self.adapter = blender_adapter or BlenderAdapter()
        self.executor = PlanExecutor(self.tx_manager, self.adapter)

        # 3. Validation & History
        self.validator = QualityGateValidator()
        self.snapshot_mgr = SnapshotManager()
        self.version_mgr = VersionManager()
        self.op_log = OperationLog()

        # 4. APIs
        self.asset_api = AssetAPI(
            self.asset_manager, self.planner, self.executor,
            self.validator, self.snapshot_mgr, self.version_mgr, self.op_log
        )
        self.inspection_api = InspectionAPI(self.state_manager)
        self.modification_api = ModificationAPI(
            self.state_manager, self.planner, self.executor,
            self.validator, self.snapshot_mgr, self.version_mgr, self.op_log
        )
        self.validation_api = ValidationAPI(self.state_manager, self.validator)
        self.plan_api = PlanAPI(self.state_manager, self.plan_generator, self.executor)

    # Fachada Pública
    def create_asset(self, spec_input: Union[Dict[str, Any], str], dry_run: bool = False) -> Dict[str, Any]:
        return self.asset_api.create_asset(spec_input, dry_run=dry_run)

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        graph = self.state_manager.get_graph(asset_id)
        return graph.to_dict() if graph else None

    def inspect_asset(self, asset_id: str) -> Dict[str, Any]:
        return self.inspection_api.inspect_asset(asset_id)

    def inspect_component(self, asset_id: str, component_id: str) -> Dict[str, Any]:
        return self.inspection_api.inspect_component(asset_id, component_id)

    def plan_intent(
        self,
        request: Union[str, Dict[str, Any]],
        active_asset_id: Optional[str] = None,
        scope: Optional[ScopeSpec] = None,
        budget: Optional[ChangeBudget] = None
    ) -> Dict[str, Any]:
        """Fase 2: Transforma lenguaje natural en plan validado sin tocar Blender."""
        return self.plan_api.plan_intent(request, active_asset_id, scope, budget)

    def explain_plan(self, plan: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """Fase 2: Genera explicación estructurada y legible de un plan."""
        return self.plan_api.explain_plan(plan)

    def plan_change(
        self,
        asset_id: str,
        target_component: str,
        changes: Dict[str, Any],
        budget: Optional[ChangeBudget] = None
    ) -> Dict[str, Any]:
        return self.modification_api.plan_change(asset_id, target_component, changes, budget)

    def apply_change(
        self,
        asset_id: str,
        target_component: str,
        changes: Dict[str, Any],
        budget: Optional[ChangeBudget] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        return self.modification_api.apply_change(asset_id, target_component, changes, budget, dry_run)

    def validate_asset(self, asset_id: str) -> Dict[str, Any]:
        return self.validation_api.validate_asset(asset_id)

    def rollback(self, asset_id: str, target_version: int) -> Dict[str, Any]:
        graph = self.rollback_mgr.get_snapshot(asset_id, target_version)
        if not graph:
            return {"success": False, "error_code": "SNAPSHOT_NOT_FOUND", "message": f"Snapshot for version {target_version} not found."}
        
        self.state_manager.active_scene_graphs[asset_id] = graph
        return {"success": True, "asset_id": asset_id, "restored_version": target_version}

    def get_history(self, asset_id: Optional[str] = None) -> list:
        return self.op_log.get_history(asset_id)
