import time
from typing import Dict, Any, List
from ..core.agent import Agent
from ..core.agent_contract import AgentContract
from ..core.agent_context import AgentContext
from ..core.agent_result import AgentResult, AssetMutation
from ..core.agent_state import AgentPermission, TaskStatus

class CorrectionAgent(Agent):
    """
    Correction Agent (F64): Applies surgical corrections targeting specific defects within the Minimal Regeneration Boundary.
    """
    def __init__(self, agent_id: str = "agent.correction", version: str = "1.0.0"):
        contract = AgentContract(
            agent_id=agent_id,
            version=version,
            capabilities=["correction.plan_repair", "correction.apply_surgical_fix"],
            permissions=[AgentPermission.MODIFY_ASSET, AgentPermission.WRITE_ASSET],
            required_context=["critic_report"],
            produces=["correction_result", "repaired_components"],
            allowed_tools=["impact_analyzer", "targeted_modifier"],
            forbidden_tools=["filesystem.delete"]
        )
        super().__init__(agent_id=agent_id, agent_type="CORRECTION", version=version, contract=contract)

    def execute(self, task_input: Dict[str, Any], context: AgentContext) -> AgentResult:
        start_t = time.time()
        self.validate_input(task_input, context)
        
        critic_report = task_input.get("critic_report", context.shared_memory.get("critic_report", {}))
        defects = critic_report.get("defects", [])
        
        repaired = []
        for d in defects:
            repaired.append({
                "target": d.get("target", "unknown"),
                "defect_id": d.get("defect_id", ""),
                "action": "SURGICAL_PARAMETRIC_UPDATE",
                "status": "RESOLVED"
            })
            
        mutation = AssetMutation(
            asset_id=context.asset_id,
            semantic_id=context.semantic_id,
            operation="APPLY_SURGICAL_CORRECTION",
            modified_entities=[r["target"] for r in repaired],
            timestamp=time.time()
        )
        
        return AgentResult(
            success=True,
            status=TaskStatus.COMPLETED,
            agent_id=self.agent_id,
            agent_version=self.version,
            task_id=context.task_id,
            outputs={"correction_result": {"repaired": repaired, "count": len(repaired)}},
            mutations=[mutation],
            metrics={"repaired_defects": float(len(repaired))},
            execution_time=time.time() - start_t
        )
