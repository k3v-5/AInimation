import copy
from typing import Dict, Any, List, Optional, Set
from ..core.guardrail_types import SkeletalDiscrepancyType, RemediationStrategy
from ..core.guardrail_schema import (
    BoneNode, SkeletalHierarchySpec, SkeletalDiscrepancy,
    SkeletalReconciliationResult
)

class SkeletalHierarchyGuard:
    """
    Agnostic guardrail that enforces skeletal hierarchy completeness.
    Ensures master skeletons contain all bones required by meshes and animations,
    detects cycles, reconciles missing bones, and produces auto-save manifests.
    """

    def validate_and_reconcile(
        self,
        master_skeleton: SkeletalHierarchySpec,
        mesh_skeletons: Optional[List[SkeletalHierarchySpec]] = None,
        anim_bone_sets: Optional[Dict[str, List[str]]] = None
    ) -> SkeletalReconciliationResult:
        discrepancies: List[SkeletalDiscrepancy] = []
        mutations: List[str] = []

        if mesh_skeletons is None:
            mesh_skeletons = []
        if anim_bone_sets is None:
            anim_bone_sets = {}

        # 1. Cycle Detection in Master Skeleton
        has_cycle, cyclic_bone = self._detect_cycle(master_skeleton)
        if has_cycle:
            discrepancies.append(
                SkeletalDiscrepancy(
                    discrepancy_type=SkeletalDiscrepancyType.CYCLIC_HIERARCHY,
                    bone_name=cyclic_bone,
                    source=master_skeleton.skeleton_id,
                    message=f"Cyclic bone hierarchy detected starting at '{cyclic_bone}' in '{master_skeleton.skeleton_id}'"
                )
            )

        # Clone skeleton for safe reconciliation
        reconciled = SkeletalHierarchySpec(
            skeleton_id=master_skeleton.skeleton_id,
            bones={k: copy.deepcopy(v) for k, v in master_skeleton.bones.items()},
            root_bone=master_skeleton.root_bone
        )

        # 2. Check Meshes for Missing Bones and Mismatched Parents
        for mesh_spec in mesh_skeletons:
            for bone_name, mesh_bone in mesh_spec.bones.items():
                if not reconciled.has_bone(bone_name):
                    discrepancies.append(
                        SkeletalDiscrepancy(
                            discrepancy_type=SkeletalDiscrepancyType.MISSING_BONE,
                            bone_name=bone_name,
                            source=mesh_spec.skeleton_id,
                            message=f"Bone '{bone_name}' required by mesh '{mesh_spec.skeleton_id}' is missing from skeleton '{master_skeleton.skeleton_id}'",
                            expected_parent=mesh_bone.parent,
                            suggested_remediation=RemediationStrategy.AUTO_SYNTHESIZE
                        )
                    )
                    # Auto-Synthesize: Inject missing bone into reconciled hierarchy
                    parent = mesh_bone.parent
                    if parent and not reconciled.has_bone(parent):
                        parent = reconciled.root_bone

                    injected_bone = copy.deepcopy(mesh_bone)
                    injected_bone.parent = parent
                    reconciled.add_bone(injected_bone)
                    mutations.append(
                        f"Injected missing bone '{bone_name}' (parent='{parent}') from mesh '{mesh_spec.skeleton_id}' into skeleton '{reconciled.skeleton_id}'"
                    )
                else:
                    # Bone exists: check parent consistency
                    existing_bone = reconciled.bones[bone_name]
                    if mesh_bone.parent and existing_bone.parent and mesh_bone.parent != existing_bone.parent:
                        discrepancies.append(
                            SkeletalDiscrepancy(
                                discrepancy_type=SkeletalDiscrepancyType.MISMATCHED_PARENT,
                                bone_name=bone_name,
                                source=mesh_spec.skeleton_id,
                                message=f"Bone '{bone_name}' parent mismatch: skeleton has '{existing_bone.parent}', mesh expects '{mesh_bone.parent}'",
                                expected_parent=mesh_bone.parent,
                                suggested_remediation=RemediationStrategy.AUTO_SYNTHESIZE
                            )
                        )

        # 3. Check Animation Bone Sets
        for anim_id, anim_bones in anim_bone_sets.items():
            for bone_name in anim_bones:
                if not reconciled.has_bone(bone_name):
                    discrepancies.append(
                        SkeletalDiscrepancy(
                            discrepancy_type=SkeletalDiscrepancyType.MISSING_BONE,
                            bone_name=bone_name,
                            source=f"anim:{anim_id}",
                            message=f"Bone '{bone_name}' animated by '{anim_id}' is missing from skeleton '{master_skeleton.skeleton_id}'",
                            expected_parent=reconciled.root_bone,
                            suggested_remediation=RemediationStrategy.AUTO_SYNTHESIZE
                        )
                    )
                    # Inject orphan bone under root
                    injected_bone = BoneNode(
                        name=bone_name,
                        parent=reconciled.root_bone,
                        head=(0.0, 0.0, 0.0),
                        tail=(0.0, 0.0, 0.1)
                    )
                    reconciled.add_bone(injected_bone)
                    mutations.append(
                        f"Injected missing animated bone '{bone_name}' under root '{reconciled.root_bone}' from anim '{anim_id}'"
                    )

        auto_save_required = len(mutations) > 0
        is_valid = (len(discrepancies) == 0)

        return SkeletalReconciliationResult(
            is_valid=is_valid,
            discrepancies=discrepancies,
            reconciled_skeleton=reconciled,
            mutations_applied=mutations,
            auto_save_required=auto_save_required
        )

    def _detect_cycle(self, skeleton: SkeletalHierarchySpec) -> (bool, str):
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def dfs(bone_name: str) -> bool:
            visited.add(bone_name)
            recursion_stack.add(bone_name)

            bone = skeleton.bones.get(bone_name)
            if bone and bone.parent:
                parent = bone.parent
                if parent in skeleton.bones:
                    if parent not in visited:
                        if dfs(parent):
                            return True
                    elif parent in recursion_stack:
                        return True

            recursion_stack.remove(bone_name)
            return False

        for bone_name in skeleton.bones:
            if bone_name not in visited:
                if dfs(bone_name):
                    return True, bone_name

        return False, ""

    @staticmethod
    def generate_engine_save_instructions(reconciliation_result: SkeletalReconciliationResult, skeleton_asset_path: str) -> Dict[str, Any]:
        """
        Produces engine-agnostic persistence payload for automations.
        """
        return {
            "skeleton_asset_path": skeleton_asset_path,
            "auto_save_required": reconciliation_result.auto_save_required,
            "mutations_count": len(reconciliation_result.mutations_applied),
            "mutations": reconciliation_result.mutations_applied,
            "missing_bones_reconciled": [
                d.bone_name for d in reconciliation_result.discrepancies
                if d.discrepancy_type == SkeletalDiscrepancyType.MISSING_BONE
            ]
        }
