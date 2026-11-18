"""Universal Production Golden Vertical Slice & Autonomous Certification System (UAF-81.88)."""

from uaf.golden_slice.manifest.models import (
    QualityProfile,
    CertificationLevel,
    PlatformType,
    BuildState,
    WorldConfig,
    PlayerConfig,
    EnemyConfig,
    GameplayConfig,
    MultiplayerConfig,
    PerformanceBudgetConfig,
    GoldenSliceManifest,
)
from uaf.golden_slice.manifest.seeds import SeedManager
from uaf.golden_slice.planner.tasks import GenerationTask, TaskType
from uaf.golden_slice.planner.graph import GenerationDAG, CyclicDependencyError
from uaf.golden_slice.generator.world import WorldGenerator, WorldSlice, SpawnPoint
from uaf.golden_slice.generator.character import CharacterGenerator, CharacterSlice, CharacterProfile
from uaf.golden_slice.generator.gameplay import GameplayGenerator, GameplaySlice, CombatAction, InventoryItem, ObjectiveState
from uaf.golden_slice.generator.vfx import VFXGenerator, VFXSlice, NiagaraSystemDescriptor
from uaf.golden_slice.generator.audio import AudioGenerator, AudioSlice, SoundCueDescriptor
from uaf.golden_slice.generator.cinematic import CinematicGenerator, CinematicSlice, CinematicKeyframe
from uaf.golden_slice.generator.ui import UIGenerator, UISlice, AccessibilitySettings
from uaf.golden_slice.scenarios.scenario import ScenarioStep, ScenarioDefinition
from uaf.golden_slice.scenarios.definitions import (
    create_golden_main_scenario,
    create_extended_stress_scenario,
    create_determinism_scenario,
    create_recovery_scenario,
)
from uaf.golden_slice.bots.player_bot import GoldenSliceBot, BotActionResult, BotExecutionReport
from uaf.golden_slice.qa.test_cases import QATestResult
from uaf.golden_slice.qa.runner import QARunner, QASuiteReport
from uaf.golden_slice.determinism.replay import TraceRecord, ReplayEngine
from uaf.golden_slice.determinism.verifier import (
    DeterminismRunResult,
    DeterminismComparisonReport,
    DeterminismVerifier,
)
from uaf.golden_slice.performance.budget import PerformanceBudget, BudgetComplianceReport
from uaf.golden_slice.performance.profiler import (
    GoldenSliceProfiler,
    ProfilingSummary,
    SubsystemFrameCost,
)
from uaf.golden_slice.networking.replication_test import (
    MultiplayerReplicationHarness,
    NetworkClientState,
    MultiplayerTestReport,
)
from uaf.golden_slice.visual.regression import (
    VisualDiffResult,
    VisualRegressionReport,
    VisualRegressionVerifier,
)
from uaf.golden_slice.audio.regression import (
    AudioEventMetric,
    AudioRegressionReport,
    AudioRegressionVerifier,
)
from uaf.golden_slice.repair.analyzer import FailureDiagnosis, FailureAnalyzer
from uaf.golden_slice.repair.knowledge_base import KnowledgeEntry, FailureKnowledgeBase
from uaf.golden_slice.repair.engine import (
    RegressionTestRecord,
    RepairExecutionResult,
    SelfRepairEngine,
)
from uaf.golden_slice.packaging.manifest import ArtifactEntry, ArtifactManifest, BuildManifest
from uaf.golden_slice.packaging.builder import CookValidationResult, PackageResult, SlicePackager
from uaf.golden_slice.packaging.bundle_exporter import UE5BundleExporter
from uaf.golden_slice.certification.gates import (
    GateEvaluation,
    GatekeeperResult,
    CertificationGatekeeper,
)
from uaf.golden_slice.certification.report import GoldenSliceCertificationReport
from uaf.golden_slice.reporting.html_report import HTMLReportGenerator
from uaf.golden_slice.artifacts.evidence import EvidencePackage
from uaf.golden_slice.artifacts.failure import FailureArtifact
from uaf.golden_slice.orchestrator.orchestrator import GoldenSliceOrchestrator
from uaf.golden_slice.cli import run_cli

__all__ = [
    "QualityProfile",
    "CertificationLevel",
    "PlatformType",
    "BuildState",
    "WorldConfig",
    "PlayerConfig",
    "EnemyConfig",
    "GameplayConfig",
    "MultiplayerConfig",
    "PerformanceBudgetConfig",
    "GoldenSliceManifest",
    "SeedManager",
    "GenerationTask",
    "TaskType",
    "GenerationDAG",
    "CyclicDependencyError",
    "WorldGenerator",
    "WorldSlice",
    "SpawnPoint",
    "CharacterGenerator",
    "CharacterSlice",
    "CharacterProfile",
    "GameplayGenerator",
    "GameplaySlice",
    "CombatAction",
    "InventoryItem",
    "ObjectiveState",
    "VFXGenerator",
    "VFXSlice",
    "NiagaraSystemDescriptor",
    "AudioGenerator",
    "AudioSlice",
    "SoundCueDescriptor",
    "CinematicGenerator",
    "CinematicSlice",
    "CinematicKeyframe",
    "UIGenerator",
    "UISlice",
    "AccessibilitySettings",
    "ScenarioStep",
    "ScenarioDefinition",
    "create_golden_main_scenario",
    "create_extended_stress_scenario",
    "create_determinism_scenario",
    "create_recovery_scenario",
    "GoldenSliceBot",
    "BotActionResult",
    "BotExecutionReport",
    "QATestResult",
    "QARunner",
    "QASuiteReport",
    "TraceRecord",
    "ReplayEngine",
    "DeterminismRunResult",
    "DeterminismComparisonReport",
    "DeterminismVerifier",
    "PerformanceBudget",
    "BudgetComplianceReport",
    "GoldenSliceProfiler",
    "ProfilingSummary",
    "SubsystemFrameCost",
    "MultiplayerReplicationHarness",
    "NetworkClientState",
    "MultiplayerTestReport",
    "VisualDiffResult",
    "VisualRegressionReport",
    "VisualRegressionVerifier",
    "AudioEventMetric",
    "AudioRegressionReport",
    "AudioRegressionVerifier",
    "FailureDiagnosis",
    "FailureAnalyzer",
    "KnowledgeEntry",
    "FailureKnowledgeBase",
    "RegressionTestRecord",
    "RepairExecutionResult",
    "SelfRepairEngine",
    "ArtifactEntry",
    "ArtifactManifest",
    "BuildManifest",
    "CookValidationResult",
    "PackageResult",
    "SlicePackager",
    "UE5BundleExporter",
    "GateEvaluation",
    "GatekeeperResult",
    "CertificationGatekeeper",
    "GoldenSliceCertificationReport",
    "HTMLReportGenerator",
    "EvidencePackage",
    "FailureArtifact",
    "GoldenSliceOrchestrator",
    "run_cli",
]
