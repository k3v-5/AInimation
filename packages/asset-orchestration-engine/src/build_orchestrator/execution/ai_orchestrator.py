from typing import Dict, Any, List, Optional, Tuple, Set
from ..core.orchestrator_types import TaskState, LockType, ExecutionMode
from ..core.orchestrator_schema import (
    Task, Checkpoint, ExecutionReport, OrchestratorConfig, OrchestrationCorrectionPlan
)
from ..agents.agent_registry import AgentRegistry
from ..agents.correction_agent import CorrectionAgent
from ..governance.task_manager import TaskManager, AssetLockManager
from ..governance.checkpoint_manager import CheckpointManager, ReworkDetector

class AIOrchestrator:
    """
    AI Build Orchestrator & Multi-Agent Execution Engine (AOE v30)
    
    Regla Fundamental:
    NINGÚN AGENTE TIENE CONTROL GLOBAL DEL PROYECTO.
    EL ORCHESTRATOR ES LA AUTORIDAD CENTRAL: COORDINA AGENTES ESPECIALISTAS, IMPONE LÍMITES DE REINTENTO,
    AISLA RECONSTRUCCIONES AL SUBÁRBOL AFECTADO Y REALIZA ROLLBACK ANTE DEGRADACIÓN O RETRABAJO.
    """
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self.registry = AgentRegistry()
        self.task_mgr = TaskManager()
        self.lock_mgr = AssetLockManager()
        self.checkpoint_mgr = CheckpointManager()
        self.rework_detector = ReworkDetector(max_attempts=self.config.max_attempts_per_task)

    def execute_asset_build(
        self,
        asset_id: str,
        initial_parameters: Dict[str, Any],
        simulated_qa_error: Optional[str] = None
    ) -> ExecutionReport:
        logs = []
        parameters = dict(initial_parameters)
        rollbacks = 0
        total_attempts = 1

        # 1. Crear Tareas y Grafo de Dependencias
        t_walls = self.task_mgr.create_task("T_WALLS", "CREATE_WALLS", asset_id)
        t_roof = self.task_mgr.create_task("T_ROOF", "CREATE_ROOF", asset_id, parent_task_id="T_WALLS")
        t_door = self.task_mgr.create_task("T_DOOR", "CREATE_DOOR", asset_id, parent_task_id="T_WALLS")
        t_qa = self.task_mgr.create_task("T_QA", "VALIDATE_GAMEPLAY", asset_id, parent_task_id="T_DOOR")

        self.task_mgr.add_dependency("T_ROOF", "T_WALLS")
        self.task_mgr.add_dependency("T_DOOR", "T_WALLS")
        self.task_mgr.add_dependency("T_QA", "T_DOOR")

        # 2. Checkpoint Obligatorio de Seguridad
        cp_init = self.checkpoint_mgr.create_checkpoint(
            f"cp_{asset_id}_init", asset_id, parameters, {t.task_id: t.state for t in self.task_mgr.tasks.values()}
        )
        logs.append(f"1. CHECKPOINT: Snapshot '{cp_init.checkpoint_id}' created before execution.")

        # 3. Adquirir Bloqueo Exclusivo de Construcción
        self.lock_mgr.acquire_lock(asset_id, "ai_orchestrator", LockType.WRITE)

        # 4. Ejecución Inicial de Tareas
        self.task_mgr.transition_state("T_WALLS", TaskState.PASSED)
        self.task_mgr.transition_state("T_ROOF", TaskState.PASSED)
        self.task_mgr.transition_state("T_DOOR", TaskState.PASSED)
        logs.append("2. EXECUTE: Walls, Roof, and Door built successfully.")

        current_error = simulated_qa_error

        # 5. Bucle de Validación y Corrección Quirúrgica (Max 3 Intentos)
        while current_error and total_attempts <= self.config.max_attempts_per_task:
            logs.append(f"3. QA_VALIDATION (Attempt {total_attempts}): Found error '{current_error}'.")
            
            # Detectar retrabajo / oscilaciones
            should_stop, reason = self.rework_detector.record_attempt("T_DOOR", "door_width", parameters.get("door_width"))
            if should_stop and total_attempts >= self.config.max_attempts_per_task:
                logs.append(f"4. ESCALATION: {reason}")
                # Rollback automático a estado seguro
                restored = self.checkpoint_mgr.restore_checkpoint(cp_init.checkpoint_id)
                if restored:
                    parameters = dict(restored.parameters)
                    rollbacks += 1
                    logs.append(f"5. ROLLBACK: Reverted asset '{asset_id}' to checkpoint '{cp_init.checkpoint_id}'.")
                
                self.lock_mgr.release_lock(asset_id, "ai_orchestrator")
                return ExecutionReport(
                    execution_id=f"exec_{asset_id}",
                    status="ROLLED_BACK",
                    tasks_executed=len(self.task_mgr.tasks),
                    total_attempts=total_attempts,
                    rollbacks_count=rollbacks,
                    final_parameters=parameters,
                    execution_logs=logs,
                    is_approved=False
                )

            # Generar plan de corrección de subárbol aislado
            plan = CorrectionAgent.generate_correction_plan(current_error, parameters)
            if plan:
                logs.append(f"   * CorrectionAgent proposed: Modify '{plan.parameter_to_change}' ({plan.old_value} -> {plan.new_value}) on subtree {plan.affected_subtrees}. (Walls & Roof untouched).")
                parameters[plan.parameter_to_change] = plan.new_value
                # Simular resolución exitosa tras aplicar corrección
                current_error = None
            
            total_attempts += 1

        # 6. Finalización y Aprobación
        self.task_mgr.transition_state("T_QA", TaskState.COMPLETED)
        self.lock_mgr.release_lock(asset_id, "ai_orchestrator")
        logs.append("6. COMMIT: Asset passed all QA validations. Final state locked and approved.")

        return ExecutionReport(
            execution_id=f"exec_{asset_id}",
            status="APPROVED",
            tasks_executed=len(self.task_mgr.tasks),
            total_attempts=total_attempts,
            rollbacks_count=rollbacks,
            final_parameters=parameters,
            execution_logs=logs,
            is_approved=True
        )
