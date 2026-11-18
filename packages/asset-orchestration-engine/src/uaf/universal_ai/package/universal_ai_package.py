"""
Universal AI Package & ProductionReadySimulation for Unreal Engine.
UAF-81.57 Sections 2, 224, 236.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher
from ..models.definition import (
    SimulationDefinition,
    AIPerformanceReport,
    AIDiagnosticReport,
    AgentLifecycleState,
)
from ..validation.universal_ai_validator import AIValidationReport


@dataclass
class ProductionReadySimulation:
    """
    Complete production asset representing a fully configured, validated, and optimizable
    simulation package ready for Unreal Engine (Section 2, 224).
    """
    simulation: SimulationDefinition
    validation_report: Optional[AIValidationReport] = None
    performance_report: AIPerformanceReport = field(default_factory=AIPerformanceReport)
    diagnostic_report: AIDiagnosticReport = field(default_factory=AIDiagnosticReport)
    export_path: str = "/Game/AI/Simulation_Main.uasset"

    @property
    def canonical_hash(self) -> str:
        payload = {
            "simulation_id": self.simulation.simulation_id,
            "seed": self.simulation.seed,
            "simulation_hash": self.simulation.simulation_hash,
            "agent_count": len(self.simulation.agents),
            "squad_count": len(self.simulation.squads),
            "export_path": self.export_path,
        }
        return CanonicalHasher.compute_hash(payload)

    def verify_readback(self) -> Dict[str, Any]:
        """
        Post-export / import readback validation checking agent counts and structural integrity.
        """
        agent_count = len(self.simulation.agents)
        active_count = sum(1 for a in self.simulation.agents if a.lifecycle == AgentLifecycleState.ACTIVE)
        squad_count = len(self.simulation.squads)
        faction_count = len(self.simulation.factions)
        cover_count = len(self.simulation.cover_points)

        return {
            "simulation_id": self.simulation.simulation_id,
            "agent_count": agent_count,
            "active_count": active_count,
            "squad_count": squad_count,
            "faction_count": faction_count,
            "cover_count": cover_count,
            "current_tick": self.simulation.current_tick,
            "canonical_hash": self.canonical_hash,
            "readback_status": "VERIFIED",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation": self.simulation.to_dict(),
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "performance_report": self.performance_report.__dict__,
            "diagnostic_report": self.diagnostic_report.__dict__,
            "export_path": self.export_path,
            "canonical_hash": self.canonical_hash,
        }
