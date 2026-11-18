"""
UAF-81.96: Autonomous Gameplay Playtesting & AI QA Simulation Package.
"""

from .core.contracts import (
    PlaytestArchetype,
    SimulationOutcome,
    SoftlockType,
    SoftlockSeverity,
    TelemetryEventType,
    HeatmapMetric,
    Vector3D,
    AgentStats,
    ArchetypeProfile,
    TelemetryEvent,
    EnemySpawn,
    DoorConnection,
    RoomSpec,
    PlaytestLevelSpec,
    SoftlockIncident,
    DifficultySpikeIncident,
    HeatmapGrid2D,
    PlaytestRunResult,
    QASimulationSuiteSummary,
)
from .agent.headless_agent import HeadlessPlaytestAgent
from .telemetry.heatmap_generator import SpatialHeatmapGenerator
from .analysis.softlock_detector import SoftlockAndDifficultyAnalyzer
from .pacing.closed_loop_calibrator import ClosedLoopPacingCalibrator
from .export.qa_report_exporter import QAReportExporter

__all__ = [
    "PlaytestArchetype",
    "SimulationOutcome",
    "SoftlockType",
    "SoftlockSeverity",
    "TelemetryEventType",
    "HeatmapMetric",
    "Vector3D",
    "AgentStats",
    "ArchetypeProfile",
    "TelemetryEvent",
    "EnemySpawn",
    "DoorConnection",
    "RoomSpec",
    "PlaytestLevelSpec",
    "SoftlockIncident",
    "DifficultySpikeIncident",
    "HeatmapGrid2D",
    "PlaytestRunResult",
    "QASimulationSuiteSummary",
    "HeadlessPlaytestAgent",
    "SpatialHeatmapGenerator",
    "SoftlockAndDifficultyAnalyzer",
    "ClosedLoopPacingCalibrator",
    "QAReportExporter",
]
