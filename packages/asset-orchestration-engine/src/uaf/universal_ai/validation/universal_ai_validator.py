"""
Universal AI Validator for UAF-81.57.
Enforces multi-factor quality scoring, category rules, and non-negotiable Hard Fail conditions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import re
from ..models.definition import (
    SimulationDefinition,
    AIAgent,
    AgentLifecycleState,
    BTNodeType,
)


@dataclass
class AIValidationReport:
    is_valid: bool = True
    quality_score: float = 100.0
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": round(self.quality_score, 2),
            "passed_checks": list(self.passed_checks),
            "failed_checks": list(self.failed_checks),
            "warnings": list(self.warnings),
            "details": dict(self.details),
        }


class UniversalAIValidator:
    """
    Quality gate & structural validator for UAF-81.57 AI & Simulation Assets.
    """

    WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:[/\\]")

    @classmethod
    def validate_simulation(
        cls,
        simulation: SimulationDefinition,
        export_path: Optional[str] = None,
    ) -> AIValidationReport:
        report = AIValidationReport()
        deductions = 0.0

        # --- 1. HARD FAIL: PATH PURITY ---
        if export_path and cls.WINDOWS_DRIVE_PATTERN.match(export_path):
            report.is_valid = False
            report.failed_checks.append(f"HARD_FAIL: Machine-dependent path detected: {export_path}")
            report.quality_score = 0.0
            return report

        for agent in simulation.agents:
            if cls.WINDOWS_DRIVE_PATTERN.match(agent.agent_id):
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Machine-dependent agent identifier: {agent.agent_id}")
                report.quality_score = 0.0
                return report

        report.passed_checks.append("CHECK_PATH_PURITY")

        # --- 2. HARD FAIL: AGENTS NOT EMPTY ---
        if not simulation.agents:
            report.is_valid = False
            report.failed_checks.append("HARD_FAIL: Simulation contains 0 agents.")
            report.quality_score = 0.0
            return report
        report.passed_checks.append("CHECK_AGENTS_NOT_EMPTY")

        # --- 3. HARD FAIL: DEAD AGENT ACTING ---
        for agent in simulation.agents:
            if agent.lifecycle == AgentLifecycleState.DEAD and agent.state.current_action != "DEAD":
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Dead agent {agent.agent_id} executing action {agent.state.current_action}")
                report.quality_score = 0.0
                return report
        report.passed_checks.append("CHECK_AGENT_LIFECYCLE_SANITY")

        # --- 4. HARD FAIL: FSM INTEGRITY ---
        for agent in simulation.agents:
            if agent.fsm:
                if agent.fsm.initial_state not in agent.fsm.states:
                    report.is_valid = False
                    report.failed_checks.append(f"HARD_FAIL: FSM initial state '{agent.fsm.initial_state}' missing in states dict.")
                    report.quality_score = 0.0
                    return report
                for trans in agent.fsm.transitions:
                    if trans.source_state not in agent.fsm.states or trans.target_state not in agent.fsm.states:
                        report.is_valid = False
                        report.failed_checks.append(f"HARD_FAIL: FSM transition {trans.source_state}->{trans.target_state} references undefined state.")
                        report.quality_score = 0.0
                        return report
        report.passed_checks.append("CHECK_FSM_GRAPH_SANITY")

        # --- 5. HARD FAIL: BEHAVIOR TREE ROOT SANITY ---
        for agent in simulation.agents:
            if agent.behavior_tree:
                if agent.behavior_tree.root_node_id not in agent.behavior_tree.nodes:
                    report.is_valid = False
                    report.failed_checks.append(f"HARD_FAIL: BT root node '{agent.behavior_tree.root_node_id}' missing in nodes dict.")
                    report.quality_score = 0.0
                    return report
        report.passed_checks.append("CHECK_BT_ROOT_SANITY")

        # --- 6. AGENT HEALTH & STAMINA BOUNDS ---
        for agent in simulation.agents:
            if agent.state.health < 0.0 or agent.state.stamina < 0.0:
                report.warnings.append(f"Agent {agent.agent_id} has negative health or stamina")
                deductions += 5.0
            else:
                report.passed_checks.append(f"CHECK_AGENT_STATS_{agent.agent_id}")

        # --- 7. SQUAD FORMATION VALIDATION ---
        for squad in simulation.squads:
            if squad.leader_id not in [a.agent_id for a in simulation.agents]:
                report.warnings.append(f"Squad {squad.squad_id} leader {squad.leader_id} not present in simulation agents")
                deductions += 10.0
            else:
                report.passed_checks.append(f"CHECK_SQUAD_{squad.squad_id}")

        report.quality_score = max(0.0, 100.0 - deductions)
        return report
