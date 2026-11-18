"""
Universal Runtime Animation Packager (UAF-81.80).
Packages animation runtime definitions, skeletons, clips, blend trees, state machines,
and generates metadata manifests compatible with Unreal Engine 5 AnimBP and Control Rig.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from ..models.definition import (
    AnimationWorld,
    copy_dict_deterministic,
)


class UniversalRuntimeAnimationPackager:
    """
    Authoritative packager creating deployment bundles and UE5 Subsystem manifests
    for runtime animation worlds.
    """

    @classmethod
    def package_world(cls, world: AnimationWorld, target_engine: str = "UNREAL_ENGINE_5") -> Dict[str, Any]:
        timestamp = time.time()
        pkg_id = f"pkg_anim_{world.animation_world_id}_{int(timestamp * 1000)}"

        world_dict = world.to_dict()

        # Build UE5-specific subsystem exports
        ue5_export = cls._generate_ue5_manifest(world)

        package_payload = {
            "package_id": pkg_id,
            "version": "1.0.0",
            "target_engine": target_engine,
            "timestamp": round(float(timestamp), 6),
            "animation_world_id": world.animation_world_id,
            "runtime_world_id": world.runtime_world_id,
            "skeletons_count": len(world.skeletons),
            "clips_count": len(world.clips),
            "state_machines_count": len(world.state_machines),
            "blend_trees_count": len(world.blend_trees),
            "ik_solvers_count": len(world.ik_solvers),
            "world_data": copy_dict_deterministic(world_dict),
            "ue5_subsystem": ue5_export,
        }

        # Calculate package hash
        canonical = copy_dict_deterministic(package_payload)
        payload_bytes = json.dumps(canonical, sort_keys=True).encode("utf-8")
        package_payload["package_hash"] = hashlib.sha256(payload_bytes).hexdigest()

        return package_payload

    @classmethod
    def _generate_ue5_manifest(cls, world: AnimationWorld) -> Dict[str, Any]:
        """Generate Unreal Engine 5 Animation Blueprint and Control Rig bindings."""
        anim_blueprints: Dict[str, Any] = {}

        for sm_id, sm in world.state_machines.items():
            states_manifest = []
            for s_id, st in sm.states.items():
                states_manifest.append({
                    "StateName": st.name,
                    "MotionType": st.motion_type,
                    "MotionAsset": st.motion_id,
                    "Speed": st.speed,
                    "bLooping": st.loop,
                })

            transitions_manifest = []
            for tr in sm.transitions:
                transitions_manifest.append({
                    "SourceState": tr.source_state_id,
                    "TargetState": tr.target_state_id,
                    "CrossfadeDuration": tr.duration,
                    "bHasExitTime": tr.has_exit_time,
                    "ExitTime": tr.exit_time,
                    "ConditionsCount": len(tr.conditions),
                })

            anim_blueprints[sm_id] = {
                "AnimBlueprintClass": f"ABP_{sm.name}",
                "DefaultState": sm.default_state_id,
                "States": states_manifest,
                "Transitions": transitions_manifest,
            }

        control_rig_nodes = []
        for solver_id, solver in world.ik_solvers.items():
            control_rig_nodes.append({
                "NodeClass": f"RigUnit_{solver.solver_type.value}",
                "SolverId": solver_id,
                "RootBone": solver.root_bone_id,
                "MidBone": solver.mid_bone_id,
                "EffectorBone": solver.end_effector_bone_id,
                "Weight": solver.weight,
            })

        return {
            "SubsystemType": "UUniversalAnimationSubsystem",
            "AnimBlueprints": anim_blueprints,
            "ControlRigSolvers": control_rig_nodes,
            "SupportedEngineVersion": "5.4+",
        }
