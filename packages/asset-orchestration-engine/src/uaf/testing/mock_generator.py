"""
MockGenerator is a self-contained, deterministic generator used for core verification without external engines.
UAF-81.0 Section 54, 55, 56.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from ..core.specification.asset_specification import AssetSpecification
from ..core.context.execution_context import ExecutionContext
from ..core.operations.operation import Operation
from ..core.operations.operation_types import OperationType
from ..core.operations.operation_status import OperationStatus
from ..core.operations.operation_result import OperationResult
from ..core.artifacts.artifact import Artifact
from ..core.paths.path_resolver import UAFPathResolver
from ..core.diagnostics.metrics import OperationMetrics
from ..core.hashing.canonical_hasher import CanonicalHasher


class MockGenerator:
    """
    Deterministic mock asset generator that produces mock 3D/metadata artifacts
    for testing the entire UAF pipeline without Blender or Unreal.
    """
    PRODUCER_NAME = "UAF_MockGenerator"
    PRODUCER_VERSION = "1.0.0"

    def __init__(self, name: str = "MockGenerator"):
        self.name = name

    def execute(self, spec: AssetSpecification, context: ExecutionContext) -> OperationResult:
        """
        Executes mock asset generation deterministically based on specification and seed.
        """
        start_time = time.time()
        operation = Operation(
            operation_id=context.operation_id,
            operation_type=OperationType.GENERATE,
            asset_id=spec.identity.asset_id,
            inputs={"specification_hash": spec.specification_hash, "seed": spec.seed},
            configuration=context.configuration,
        )
        operation.transition_to(OperationStatus.READY)
        operation.transition_to(OperationStatus.RUNNING)

        resolver = UAFPathResolver(context.project_context)

        # Build mock payload deterministically
        mock_geometry = {
            "asset_urn": spec.identity.urn,
            "seed": spec.seed,
            "target": spec.target,
            "quality_profile": spec.quality_profile,
            "mesh_data": {
                "vertex_count": 8 + (spec.seed % 100),
                "face_count": 6 + (spec.seed % 50),
                "bounding_box": {"min": [-1.0, -1.0, 0.0], "max": [1.0, 1.0, 2.0]},
            },
            "parameters": spec.parameters,
        }

        # Deterministic filename and path inside artifact root
        relative_filename = f"{spec.identity.asset_id}_v{spec.identity.version}_mesh.json"
        artifact_file_path = resolver.resolve_artifact_path(relative_filename)
        artifact_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write canonical JSON payload
        payload_bytes = CanonicalHasher.to_canonical_json(mock_geometry).encode("utf-8")
        with open(artifact_file_path, "wb") as f:
            f.write(payload_bytes)

        # Build Artifact object
        artifact = Artifact.create_from_file(
            file_path=artifact_file_path,
            artifact_id=f"art_{spec.identity.asset_id}_mock_mesh",
            artifact_type="MOCK_MESH",
            asset_id=spec.identity.asset_id,
            producer=self.PRODUCER_NAME,
            producer_version=self.PRODUCER_VERSION,
            relative_path=relative_filename,
            metadata={"spec_hash": spec.specification_hash, "seed": spec.seed},
        )

        duration = time.time() - start_time
        metrics = OperationMetrics(
            duration_ms=duration * 1000.0,
            cpu_time_ms=duration * 1000.0,
            disk_write_bytes=len(payload_bytes),
            artifact_count=1,
            cache_miss=True,
        )

        operation.transition_to(OperationStatus.SUCCEEDED)

        return OperationResult(
            operation_id=operation.operation_id,
            status=OperationStatus.SUCCEEDED,
            artifacts=[artifact.to_dict()],
            diagnostics=[],
            metrics=metrics.to_dict(),
            duration_seconds=duration,
        )
