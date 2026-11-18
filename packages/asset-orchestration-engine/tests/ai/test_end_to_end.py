"""
End-to-End Simulation Pipeline & Packaging Test (UAF-81.57 Section 226).
"""

import pytest
from uaf.universal_ai import (
    UniversalAIFabricator,
    UniversalAIValidator,
    ProductionReadySimulation,
    AgentLifecycleState,
)


def test_end_to_end_simulation_lifecycle():
    # 1. Procedural Creation
    sim = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_COMBAT)
    assert sim.simulation_id == "SIM_GOLDEN_COMBAT"
    assert len(sim.agents) == 2
    assert len(sim.cover_points) == 1

    # 2. 12-Stage Simulation Execution (10 ticks)
    for _ in range(10):
        UniversalAIFabricator.execute_simulation_tick(sim, dt=0.033)

    assert sim.current_tick == 10
    # Both agents should have perceived each other and populated memory
    for agent in sim.agents:
        assert len(agent.memory.records) > 0

    # 3. Validation
    export_path = "/Game/AI/Sim_Combat_Final.uasset"
    validation_report = UniversalAIValidator.validate_simulation(sim, export_path=export_path)
    assert validation_report.is_valid is True
    assert validation_report.quality_score == 100.0

    # 4. Unreal Packaging
    package = ProductionReadySimulation(
        simulation=sim,
        validation_report=validation_report,
        export_path=export_path,
    )
    assert package.canonical_hash is not None
    assert len(package.canonical_hash) == 64

    # 5. Readback Verification
    readback = package.verify_readback()
    assert readback["simulation_id"] == "SIM_GOLDEN_COMBAT"
    assert readback["agent_count"] == 2
    assert readback["active_count"] == 2
    assert readback["cover_count"] == 1
    assert readback["current_tick"] == 10
    assert readback["canonical_hash"] == package.canonical_hash
