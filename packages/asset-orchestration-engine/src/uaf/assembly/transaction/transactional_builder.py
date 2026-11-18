"""
TransactionalAssetBuilder enforces atomic Prepare-Validate-Commit cycles with automated rollback.
UAF-81.8 Sections 102, 103, 104, 124.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..graph.assembly_graph import AssetAssemblyGraph, AssetLifecycleState
from ..spatial.pivot import PivotDefinition
from ..spatial.socket import RuntimeSocketDefinition
from ..optimization.lod_policy import LODChain, NanitePolicy
from ..validation.runtime_validator import RuntimeAssetValidator, RuntimeAssetQualityReport


@dataclass
class TransactionalAssetBuilder:
    """
    Executes atomic Prepare -> Validate -> Commit pipeline.
    Prevents corrupting previous valid outputs when builds fail.
    """
    asset_id: str
    graph: Optional[AssetAssemblyGraph] = None
    pivot: Optional[PivotDefinition] = None
    sockets: List[RuntimeSocketDefinition] = field(default_factory=list)
    lod_chain: Optional[LODChain] = None
    is_static: bool = True
    validation_report: Optional[RuntimeAssetQualityReport] = None
    is_committed: bool = False

    def prepare(
        self,
        render_components: List[str],
        material_slots: Dict[int, str],
        collision_shapes: List[str],
        physics_bodies: Optional[List[str]] = None,
        pivot: Optional[PivotDefinition] = None,
        sockets: Optional[List[RuntimeSocketDefinition]] = None,
        base_triangles: int = 4000,
    ) -> "TransactionalAssetBuilder":
        self.graph = AssetAssemblyGraph(
            asset_id=self.asset_id,
            render_components=render_components,
            material_slots=material_slots,
            collision_shapes=collision_shapes,
            physics_bodies=physics_bodies or [],
            socket_ids=[s.socket_id for s in (sockets or [])],
            lifecycle_state=AssetLifecycleState.OPTIMIZED,
        )
        self.pivot = pivot or PivotDefinition()
        self.sockets = sockets or []
        self.lod_chain = LODChain.create_standard_chain(base_triangles=base_triangles)
        return self

    def validate(self) -> RuntimeAssetQualityReport:
        if not self.graph:
            raise RuntimeError("Cannot validate un-prepared asset transaction.")

        self.validation_report = RuntimeAssetValidator.validate_assembly(
            graph=self.graph,
            pivot=self.pivot,
            sockets=self.sockets,
            lod_chain=self.lod_chain,
            is_static=self.is_static,
        )
        return self.validation_report

    def commit(self) -> bool:
        """Commits asset to PUBLISHED state only if validation passed (Section 124)."""
        if not self.validation_report or not self.validation_report.is_valid:
            self.rollback()
            return False

        if self.graph:
            self.graph.lifecycle_state = AssetLifecycleState.PUBLISHED
        self.is_committed = True
        return True

    def rollback(self) -> None:
        """Rollback on failure (Section 104)."""
        if self.graph:
            self.graph.lifecycle_state = AssetLifecycleState.REJECTED
        self.is_committed = False
