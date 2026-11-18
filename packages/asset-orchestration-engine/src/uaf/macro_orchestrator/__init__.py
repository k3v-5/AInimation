"""
UAF-81.102: Universal Macro-Orchestrator & One-Click Full Vertical Slice Builder.
Unified pipeline connecting Landscape, Spatial Solvers, WFC Modular Interiors,
Tactical AI, Volumetric Weather, Chaos Voronoi Destruction, Interactive Audio & QA Playtesting.
"""

from uaf.macro_orchestrator.core.contracts import (
    SliceSize,
    OrchestrationStage,
    SpatialFootprint,
    StageExecutionMetric,
    VerticalSliceConfig,
    IntegratedSliceManifest,
)
from uaf.macro_orchestrator.spatial.constraint_solver import SpatialConstraintSolver
from uaf.macro_orchestrator.orchestrator.slice_orchestrator import VerticalSliceMasterOrchestrator
from uaf.macro_orchestrator.integrator.package_integrator import (
    MasterPackageIntegrator,
    PackageResult,
)
from uaf.macro_orchestrator.cli.slice_cli import (
    build_vertical_slice,
    run_cli,
    create_cli_parser,
)

__all__ = [
    "SliceSize",
    "OrchestrationStage",
    "SpatialFootprint",
    "StageExecutionMetric",
    "VerticalSliceConfig",
    "IntegratedSliceManifest",
    "SpatialConstraintSolver",
    "VerticalSliceMasterOrchestrator",
    "MasterPackageIntegrator",
    "PackageResult",
    "build_vertical_slice",
    "run_cli",
    "create_cli_parser",
]
