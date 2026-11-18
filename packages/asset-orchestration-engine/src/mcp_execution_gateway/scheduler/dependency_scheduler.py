from typing import List, Dict, Any, Optional
from ..core.gateway_types import RiskLevel
from ..core.gateway_schema import GatewayCommand, CommandPlan, GatewayPolicy

class DependencyScheduler:
    @staticmethod
    def create_plan(commands: List[GatewayCommand], policy: GatewayPolicy) -> CommandPlan:
        # Calcular llamadas MCP estimadas
        estimated_calls = len(commands)
        if estimated_calls > policy.max_mcp_calls_per_operation:
            raise ValueError(f"BUDGET_EXCEEDED: Operation requires {estimated_calls} MCP calls which exceeds allowed budget ({policy.max_mcp_calls_per_operation}).")

        # Calcular nivel de riesgo general
        overall_risk = RiskLevel.LOW
        for cmd in commands:
            if cmd.risk_level == RiskLevel.CRITICAL:
                overall_risk = RiskLevel.CRITICAL
                break
            elif cmd.risk_level == RiskLevel.HIGH and overall_risk != RiskLevel.CRITICAL:
                overall_risk = RiskLevel.HIGH
            elif cmd.risk_level == RiskLevel.MEDIUM and overall_risk == RiskLevel.LOW:
                overall_risk = RiskLevel.MEDIUM

        return CommandPlan(
            plan_id="PLAN_01",
            commands=commands,
            estimated_mcp_calls=estimated_calls,
            estimated_duration=round(estimated_calls * 0.1, 2),
            overall_risk=overall_risk
        )

class ExecutionLoopGuard:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.command_counts: Dict[str, int] = {}

    def record_attempt(self, command_sig: str):
        self.command_counts[command_sig] = self.command_counts.get(command_sig, 0) + 1
        if self.command_counts[command_sig] > self.max_retries:
            raise RuntimeError(f"LOOP_DETECTED: Command '{command_sig}' repeated {self.command_counts[command_sig]} times exceeding limit.")

    def reset(self):
        self.command_counts.clear()
