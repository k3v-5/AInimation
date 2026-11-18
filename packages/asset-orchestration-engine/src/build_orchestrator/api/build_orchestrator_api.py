from typing import Dict, Any, List, Optional
from ..core.orchestrator_types import AgentType, TaskState, LockType, ExecutionMode, RiskLevel
from ..core.orchestrator_schema import (
    AgentDefinition, Task, Checkpoint, ExecutionReport, OrchestratorConfig, OrchestrationCorrectionPlan
)
from ..execution.ai_orchestrator import AIOrchestrator

class BuildOrchestratorAPI:
    """
    Build Orchestrator Public API (AOE v30)
    """
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.orchestrator = AIOrchestrator(config)

    def run_orchestrated_build(
        self,
        asset_id: str,
        initial_parameters: Dict[str, Any],
        simulated_qa_error: Optional[str] = None
    ) -> ExecutionReport:
        return self.orchestrator.execute_asset_build(
            asset_id=asset_id,
            initial_parameters=initial_parameters,
            simulated_qa_error=simulated_qa_error
        )

    def validate_tool_permission(self, agent_id: str, tool_name: str) -> bool:
        return self.orchestrator.registry.validate_tool_permission(agent_id, tool_name)

    def calculate_weapon_muzzle_and_orientation(self, mesh_obj) -> Dict[str, Any]:
        """
        Calcula la boquilla y valida orientación canónica usando WeaponMuzzleCalculator.
        """
        from ...validation.weapon_muzzle_calculator import WeaponMuzzleCalculator
        orientation_res = WeaponMuzzleCalculator.determinar_orientacion_forward(mesh_obj)
        muzzle_loc = WeaponMuzzleCalculator.calcular_posicion_boquilla(mesh_obj)
        return {
            "orientation": orientation_res,
            "muzzle_location": muzzle_loc,
            "is_canonical": orientation_res.get("es_canonico", False)
        }

AssetEngineOrchestrator = BuildOrchestratorAPI

