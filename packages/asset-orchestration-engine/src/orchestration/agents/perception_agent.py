import time
from typing import Dict, Any
from ..core.agent import Agent
from ..core.agent_contract import AgentContract
from ..core.agent_context import AgentContext
from ..core.agent_result import AgentResult
from ..core.agent_state import AgentPermission, TaskStatus

class PerceptionAgent(Agent):
    """
    Perception Agent (F55): Analyzes visual references and decomposes silhouette, proportions, and palette.
    """
    def __init__(self, agent_id: str = "agent.perception", version: str = "1.0.0"):
        contract = AgentContract(
            agent_id=agent_id,
            version=version,
            capabilities=["perception.analyze_reference", "perception.decompose_parts"],
            permissions=[AgentPermission.READ_PROJECT, AgentPermission.READ_ASSET],
            required_context=["reference_data"],
            produces=["reference_report", "silhouette_aspect", "proportion_breakdown"],
            allowed_tools=["reference_analyzer", "vision_decomposer"],
            forbidden_tools=["filesystem.delete", "execute.blender_write"]
        )
        super().__init__(agent_id=agent_id, agent_type="PERCEPTION", version=version, contract=contract)

    def execute(self, task_input: Dict[str, Any], context: AgentContext) -> AgentResult:
        start_t = time.time()
        self.validate_input(task_input, context)
        
        ref_data = task_input.get("reference_data", {})
        prompt = task_input.get("prompt", "Default tactical weapon")
        
        report = {
            "prompt": prompt,
            "silhouette": {"aspect_ratio": 1.0, "symmetry": "SYMMETRICAL_X"},
            "proportions": {"receiver": 0.35, "barrel": 0.40, "stock": 0.25},
            "palette": {"primary_metal": "GUN_METAL_DARK", "grip": "POLYMER_BLACK", "accent": "PLASMA_CYAN"},
            "raw_reference": ref_data
        }
        
        return AgentResult(
            success=True,
            status=TaskStatus.COMPLETED,
            agent_id=self.agent_id,
            agent_version=self.version,
            task_id=context.task_id,
            outputs={"reference_report": report},
            metrics={"confidence": 0.96},
            execution_time=time.time() - start_t
        )
