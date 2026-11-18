import time
from typing import Dict, Any, List, Optional
from ..core.agent_state import TaskStatus, TaskPriority, FailureAction, AgentState
from ..core.agent_registry import AgentRegistry
from ..core.agent_context import AgentContext
from ..core.agent_result import AgentResult
from ..core.orchestration_plan import OrchestrationPlan
from ..core.orchestration_policy import OrchestrationPolicy
from ..tasks.task import Task
from ..tasks.task_graph import TaskGraph
from ..scheduler.task_scheduler import TaskScheduler
from ..events.orchestration_event import OrchestrationEvent, OrchestrationEventLog
from ..core.exceptions import (
    OrchestrationError, CyclicDependencyError, ToolAccessDeniedError,
    PermissionDeniedError, AgentNotFoundError, TaskExecutionError
)
from ..agents.perception_agent import PerceptionAgent
from ..agents.design_analysis_agent import DesignAnalysisAgent
from ..agents.strategy_agent import StrategyAgent
from ..agents.geometry_agent import GeometryAgent
from ..agents.material_agent import MaterialAgent
from ..agents.blender_execution_agent import BlenderExecutionAgent
from ..agents.visual_critic_agent import VisualCriticAgent
from ..agents.qa_agent import QAAgent
from ..agents.correction_agent import CorrectionAgent
from ..agents.packaging_agent import PackagingAgent

class OrchestrationEngine:
    """
    Master Multi-Agent Orchestration Engine (F71).
    Coordinates specialized agents over DAG TaskGraphs with persistent checkpoints,
    hard-gate visual & technical quality enforcement, and iterative self-repair.
    """
    def __init__(self, registry: Optional[AgentRegistry] = None, policy: Optional[OrchestrationPolicy] = None):
        self.registry = registry or AgentRegistry()
        self._register_default_agents()
        self.policy = policy or OrchestrationPolicy()
        self.scheduler = TaskScheduler(self.registry, max_concurrency=self.policy.concurrency_limit)
        self.event_log = OrchestrationEventLog()
        self._shared_memory: Dict[str, Dict[str, Any]] = {} # orchestration_id -> shared dict

    def _register_default_agents(self):
        default_agents = [
            PerceptionAgent(),
            DesignAnalysisAgent(),
            StrategyAgent(),
            GeometryAgent(),
            MaterialAgent(),
            BlenderExecutionAgent(),
            VisualCriticAgent(),
            QAAgent(),
            CorrectionAgent(),
            PackagingAgent()
        ]
        for a in default_agents:
            if a.agent_id not in [x.agent_id for x in self.registry.list_agents()]:
                self.registry.register(a)

    def execute_plan(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        plan.task_graph.validate_graph()
        orch_id = plan.orchestration_id
        self._shared_memory[orch_id] = {}
        
        self.event_log.record(OrchestrationEvent(
            event_id=f"EVT_{orch_id}_START",
            orchestration_id=orch_id,
            event_type="ORCHESTRATION_STARTED",
            payload={"objective": plan.objective, "asset_id": plan.asset_id}
        ))

        iteration = 0
        all_completed = False
        final_results = {}

        while iteration < plan.max_iterations and not all_completed:
            schedulable = self.scheduler.get_schedulable_tasks(plan.task_graph)
            if not schedulable:
                # Check if all tasks completed or if blocked
                pending_or_running = [t for t in plan.task_graph.list_tasks() if t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.SKIPPED]]
                if not pending_or_running:
                    all_completed = True
                    break
                else:
                    # Deadlock or dependency failure
                    break

            for task in schedulable:
                task.transition_to(TaskStatus.RUNNING)
                self.scheduler.acquire_locks_for_task(task)
                
                agent = self.scheduler.assign_agent(task)
                context = AgentContext(
                    orchestration_id=orch_id,
                    job_id=f"JOB_{orch_id}",
                    task_id=task.task_id,
                    asset_id=plan.asset_id,
                    semantic_id=plan.semantic_id,
                    permissions=agent.contract.permissions,
                    available_capabilities=agent.contract.capabilities,
                    previous_results=final_results,
                    shared_memory=self._shared_memory[orch_id]
                )
                
                self.event_log.record(OrchestrationEvent(
                    event_id=f"EVT_{task.task_id}_START",
                    orchestration_id=orch_id,
                    task_id=task.task_id,
                    agent_id=agent.agent_id,
                    event_type="TASK_STARTED"
                ))

                try:
                    result = agent.execute(task.inputs, context)
                    if result.success:
                        task.outputs = result.outputs
                        self._shared_memory[orch_id].update(result.outputs)
                        final_results[task.task_id] = result
                        task.transition_to(TaskStatus.COMPLETED)
                        
                        self.event_log.record(OrchestrationEvent(
                            event_id=f"EVT_{task.task_id}_COMPLETE",
                            orchestration_id=orch_id,
                            task_id=task.task_id,
                            agent_id=agent.agent_id,
                            event_type="TASK_COMPLETED",
                            payload=result.outputs
                        ))
                    else:
                        task.transition_to(TaskStatus.FAILED)
                except Exception as e:
                    task.transition_to(TaskStatus.FAILED)
                    self.event_log.record(OrchestrationEvent(
                        event_id=f"EVT_{task.task_id}_FAIL",
                        orchestration_id=orch_id,
                        task_id=task.task_id,
                        agent_id=agent.agent_id,
                        event_type="TASK_FAILED",
                        payload={"error": str(e)}
                    ))
                finally:
                    self.scheduler.release_locks_for_task(task)

            iteration += 1

        self.event_log.record(OrchestrationEvent(
            event_id=f"EVT_{orch_id}_END",
            orchestration_id=orch_id,
            event_type="ORCHESTRATION_COMPLETED" if all_completed else "ORCHESTRATION_HALTED",
            payload={"completed_tasks": len(final_results)}
        ))

        return {
            "orchestration_id": orch_id,
            "success": all_completed,
            "completed_tasks": len(final_results),
            "results": final_results,
            "events_count": len(self.event_log.list_events(orch_id))
        }

    def build_standard_weapon_pipeline_plan(self, asset_id: str, semantic_id: str, prompt: str = "Tactical weapon") -> OrchestrationPlan:
        """Constructs the canonical 11-step multi-agent weapon generation & validation plan."""
        plan = OrchestrationPlan(
            orchestration_id=f"ORCH_{asset_id}_{int(time.time()*1000)%100000}",
            objective="Generate, evaluate, critique and package high-fidelity weapon asset",
            asset_id=asset_id,
            semantic_id=semantic_id
        )
        
        # T1: Perception
        t1 = Task(task_id="T1_Perception", task_type="PERCEPTION", description="Analyze visual references", inputs={"prompt": prompt, "reference_data": {"style": "DARX_CYBERPUNK"}})
        
        # T2: Design Analysis (depends on T1)
        t2 = Task(task_id="T2_DesignAnalysis", task_type="DESIGN_ANALYSIS", description="Compile VAS specification", dependencies=["T1_Perception"])
        
        # T3: Strategy (depends on T2)
        t3 = Task(task_id="T3_Strategy", task_type="STRATEGY", description="Plan modeling strategy", dependencies=["T2_DesignAnalysis"])
        
        # T4: Geometry (depends on T3)
        t4 = Task(task_id="T4_Geometry", task_type="GEOMETRY", description="Generate 3D mesh components", dependencies=["T3_Strategy"])
        
        # T5: Material (depends on T3 - parallel with T4)
        t5 = Task(task_id="T5_Material", task_type="MATERIAL", description="Generate PBR shader networks", dependencies=["T3_Strategy"])
        
        # T6: Blender Assembly (depends on T4, T5)
        t6 = Task(task_id="T6_BlenderAssembly", task_type="BLENDER_EXECUTION", description="Assemble scene & render in Blender", dependencies=["T4_Geometry", "T5_Material"])
        
        # T7: Visual Critic (depends on T6)
        t7 = Task(task_id="T7_VisualCritic", task_type="VISUAL_CRITIC", description="Evaluate visual quality against rubric", dependencies=["T6_BlenderAssembly"])
        
        # T8: QA (depends on T6)
        t8 = Task(task_id="T8_QA", task_type="QA_VALIDATOR", description="Technical QA topology and collision validation", dependencies=["T6_BlenderAssembly"])
        
        # T9: Packaging (depends on T7, T8)
        t9 = Task(task_id="T9_Packaging", task_type="PACKAGING", description="Seal and deliver package", dependencies=["T7_VisualCritic", "T8_QA"])
        
        for t in [t1, t2, t3, t4, t5, t6, t7, t8, t9]:
            plan.task_graph.add_task(t)
            
        return plan
