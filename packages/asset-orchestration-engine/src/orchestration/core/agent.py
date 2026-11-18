from abc import ABC, abstractmethod
import time
from typing import Dict, Any, Optional
from .agent_state import AgentState, AgentPermission, TaskStatus
from .agent_contract import AgentContract
from .agent_context import AgentContext
from .agent_result import AgentResult
from .exceptions import AgentContractViolationError, ToolAccessDeniedError, PermissionDeniedError

class Agent(ABC):
    """
    Abstract Base Class for all specialized agents in the Multi-Agent Orchestration Layer.
    """
    def __init__(self, agent_id: str, agent_type: str, version: str = "1.0.0", contract: Optional[AgentContract] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.version = version
        self.contract = contract or AgentContract(agent_id=agent_id, version=version)
        self.state: AgentState = AgentState.UNINITIALIZED

    def initialize(self, context: AgentContext):
        self.state = AgentState.IDLE

    def validate_input(self, task_input: Dict[str, Any], context: AgentContext) -> bool:
        # Check required context fields
        for req in self.contract.required_context:
            if req not in task_input and req not in context.shared_memory:
                raise AgentContractViolationError(f"Missing required context key: {req} for agent {self.agent_id}")
        return True

    def run_tool(self, tool_name: str, capability_fn, *args, **kwargs):
        if not self.contract.validate_tool_access(tool_name):
            raise ToolAccessDeniedError(f"Agent {self.agent_id} is denied access to tool {tool_name}")
        return capability_fn(*args, **kwargs)

    @abstractmethod
    def execute(self, task_input: Dict[str, Any], context: AgentContext) -> AgentResult:
        pass

    def validate_output(self, result: AgentResult, context: AgentContext) -> bool:
        if not isinstance(result, AgentResult):
            return False
        return True

    def rollback(self, result: AgentResult, context: AgentContext):
        pass

    def shutdown(self, context: Optional[AgentContext] = None):
        self.state = AgentState.SHUTDOWN
