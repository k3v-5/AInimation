from typing import Dict, Any, List, Optional, Tuple
from ..core.scene_types import SceneType, LockState, SceneState
from ..core.scene_schema import (
    SceneSpecification, SceneBuildPlan, SceneBudget, AssetInstance,
    SocketDefinition, SceneDiagnosticReport
)
from ..spatial.socket_matcher import SocketMatcher
from ..spatial.collision_validator import SceneCollisionValidator
from ..planning.hierarchical_planner import HierarchicalPlanner
from ..planning.scene_optimizer import SceneOptimizer
from ..planning.scene_quality_gate import SceneQualityGate
from ..adapter.blender_scene_adapter import BlenderSceneAdapter

class CompositeSceneAPI:
    """
    Composite Asset & Scene Construction System API (AOE v28)
    
    Regla Fundamental:
    LA IA TRABAJA CON SCENE INTENT Y NO CON COMANDOS INDIVIDUALES DE BLENDER.
    LA ESCENA SE PLANIFICA EN JERARQUÍA (MACRO -> MESO -> MICRO) CON RESOLUCIÓN ESPACIAL DETERMINISTA,
    CONTROL DE COLISIONES, ENRUTAMIENTO POR SOCKETS Y RECONSTRUCCIÓN PARCIAL AISLADA POR REGIÓN.
    """
    def __init__(self):
        self.adapter = BlenderSceneAdapter()

    def create_scene_plan(self, spec: SceneSpecification) -> SceneBuildPlan:
        plan = HierarchicalPlanner.plan_scene(spec)
        self.adapter.sync_scene_plan(plan)
        return plan

    def modify_region(
        self,
        plan: SceneBuildPlan,
        region_id: str,
        delta_x: float = 0.0,
        delta_y: float = 0.0
    ) -> List[str]:
        """
        Modifica únicamente las instancias pertenecientes a una región específica (Reconstrucción Parcial Aislada).
        """
        modified_ids = []
        for inst in plan.instances.values():
            if inst.region_id == region_id:
                if inst.lock_state in [LockState.LOCKED, LockState.PROTECTED]:
                    continue # Respetar bloqueo de objetos
                inst.transform["x"] = round(inst.transform["x"] + delta_x, 2)
                inst.transform["y"] = round(inst.transform["y"] + delta_y, 2)
                modified_ids.append(inst.instance_id)

        self.adapter.sync_scene_plan(plan)
        return modified_ids

    def align_sockets(
        self,
        source_instance: AssetInstance,
        source_socket: SocketDefinition,
        target_instance: AssetInstance,
        target_socket: SocketDefinition
    ) -> Tuple[bool, str]:
        ok, new_tf, msg = SocketMatcher.match_and_align(
            source_instance, source_socket, target_instance, target_socket
        )
        if ok:
            source_instance.transform = new_tf
        return ok, msg

    def validate_scene(
        self,
        plan: SceneBuildPlan,
        roads: List[Dict[str, float]] = None
    ) -> SceneDiagnosticReport:
        return SceneQualityGate.evaluate_scene(plan, roads)

    def optimize_scene(
        self,
        plan: SceneBuildPlan,
        simulated_triangles: int
    ) -> Tuple[bool, int, List[str]]:
        budget = SceneBudget()
        return SceneOptimizer.optimize_scene(plan, budget, simulated_triangles)

    def get_scene_fingerprint(self, plan: SceneBuildPlan, seed: int = 42) -> str:
        return HierarchicalPlanner.compute_scene_fingerprint(plan, seed)

    def set_instance_lock(self, plan: SceneBuildPlan, instance_id: str, lock_state: LockState):
        if instance_id in plan.instances:
            plan.instances[instance_id].lock_state = lock_state
            self.adapter.sync_scene_plan(plan)
