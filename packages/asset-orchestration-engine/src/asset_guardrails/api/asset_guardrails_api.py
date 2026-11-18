from typing import List, Dict, Any, Optional, Callable, Tuple
from ..core.guardrail_schema import (
    SkeletalHierarchySpec, SkeletalReconciliationResult,
    EntitySpatialSpec, SpatialClearanceResult,
    SurfacePlaneSpec, CoplanarRemediationResult
)
from ..guards.skeletal_hierarchy_guard import SkeletalHierarchyGuard
from ..guards.spatial_clearance_guard import SpatialClearanceGuard
from ..guards.coplanar_surface_guard import CoplanarSurfaceGuard

class AssetGuardrailsAPI:
    """
    Unified public API for game-agnostic asset guardrails.
    Protects asset pipelines from skeletal discrepancies, entity ground clipping/overlap,
    and coplanar texture collisions / Z-fighting.
    """

    def __init__(self):
        self.skeletal_guard = SkeletalHierarchyGuard()
        self.spatial_guard = SpatialClearanceGuard()
        self.coplanar_guard = CoplanarSurfaceGuard()

    def reconcile_skeletal_hierarchy(
        self,
        master_skeleton: SkeletalHierarchySpec,
        mesh_skeletons: Optional[List[SkeletalHierarchySpec]] = None,
        anim_bone_sets: Optional[Dict[str, List[str]]] = None
    ) -> SkeletalReconciliationResult:
        """
        Validates completeness of skeleton hierarchy and reconciles any missing bones
        required by meshes or animations.
        """
        return self.skeletal_guard.validate_and_reconcile(
            master_skeleton=master_skeleton,
            mesh_skeletons=mesh_skeletons,
            anim_bone_sets=anim_bone_sets
        )

    def enforce_spatial_clearance(
        self,
        entities: List[EntitySpatialSpec],
        ground_height_sampler: Optional[Callable[[float, float], float]] = None,
        clearance_margin: float = 15.0,
        max_repulsion_iterations: int = 40
    ) -> SpatialClearanceResult:
        """
        Enforces ground datum contact and eliminates inter-entity collisions and overlaps
        using non-linear relaxation repulsion.
        """
        return self.spatial_guard.validate_and_resolve(
            entities=entities,
            ground_height_sampler=ground_height_sampler,
            clearance_margin=clearance_margin,
            max_repulsion_iterations=max_repulsion_iterations
        )

    def resolve_coplanar_surfaces(
        self,
        surfaces: List[SurfacePlaneSpec],
        plane_tolerance: float = 0.01,
        micro_offset_step: float = 0.05,
        cull_internal_faces: bool = True
    ) -> CoplanarRemediationResult:
        """
        Detects and eliminates coplanar surface collisions, applying micro-layering offsets
        or internal face culling to eradicate Z-fighting.
        """
        return self.coplanar_guard.validate_and_resolve(
            surfaces=surfaces,
            plane_tolerance=plane_tolerance,
            micro_offset_step=micro_offset_step,
            cull_internal_faces=cull_internal_faces
        )

    def audit_and_remediate_all(
        self,
        master_skeleton: Optional[SkeletalHierarchySpec] = None,
        mesh_skeletons: Optional[List[SkeletalHierarchySpec]] = None,
        anim_bone_sets: Optional[Dict[str, List[str]]] = None,
        entities: Optional[List[EntitySpatialSpec]] = None,
        surfaces: Optional[List[SurfacePlaneSpec]] = None,
        ground_height_sampler: Optional[Callable[[float, float], float]] = None
    ) -> Dict[str, Any]:
        """
        Executes a holistic audit pass across all three guardrails in a single invocation.
        """
        report: Dict[str, Any] = {
            "all_passed": True,
            "skeletal": None,
            "spatial": None,
            "coplanar": None
        }

        if master_skeleton is not None:
            skel_res = self.reconcile_skeletal_hierarchy(
                master_skeleton=master_skeleton,
                mesh_skeletons=mesh_skeletons,
                anim_bone_sets=anim_bone_sets
            )
            report["skeletal"] = skel_res
            if not skel_res.is_valid:
                report["all_passed"] = False

        if entities is not None:
            spatial_res = self.enforce_spatial_clearance(
                entities=entities,
                ground_height_sampler=ground_height_sampler
            )
            report["spatial"] = spatial_res
            if not spatial_res.is_valid:
                report["all_passed"] = False

        if surfaces is not None:
            coplanar_res = self.resolve_coplanar_surfaces(
                surfaces=surfaces
            )
            report["coplanar"] = coplanar_res
            if not coplanar_res.is_valid:
                report["all_passed"] = False

        return report
