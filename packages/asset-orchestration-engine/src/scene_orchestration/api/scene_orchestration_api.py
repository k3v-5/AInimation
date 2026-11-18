from typing import Dict, Any, Optional, Tuple, List, Set
from ..core.scene_schema import SceneIntent, ScenePlan, SceneNode, SceneSummary
from ..core.scene_status import SceneStatus, NodeDirtyState, BuildStage
from ..core.scene_graph import SceneGraph
from ..spatial.layout_solver import LayoutSolver
from ..spatial.proxy_scene import ProxyScene
from ..execution.checkpoint_manager import CheckpointManager
from ..execution.batch_builder import BatchSceneBuilder
from ..reconciliation.scene_reconciler import SceneReconciler
from ...correction_execution.providers.blender_provider import IBlenderProvider

class SceneOrchestrationAPI:
    """
    Multi-Asset & Scene Orchestration API (AOE v19)
    
    Regla Fundamental:
    LA IA NO COLOCA NI MODELA CADA OBJETO. DEFINE LA INTENCIÓN DE ESCENA.
    EL MOTOR RESUELVE: PLAN -> PROXY -> SPATIAL CHECK -> BATCH BUILD -> RECONCILIATION.
    REBUILD_RATIO MINIMIZADO (1/N) ANTE CAMBIOS AISLADOS.
    """
    def __init__(self, max_scene_assets: int = 50):
        self.max_scene_assets = max_scene_assets
        self.graphs: Dict[str, SceneGraph] = {}
        self.plans: Dict[str, ScenePlan] = {}
        self.checkpoint_manager = CheckpointManager()

    def plan_scene(self, intent: SceneIntent) -> Tuple[bool, Optional[ScenePlan], str]:
        # 1. Resolver Layout espacial
        plan = LayoutSolver.solve_layout(intent)

        # 2. Comprobar límites de presupuesto
        if len(plan.nodes) > self.max_scene_assets:
            return False, None, f"SCENE_BUDGET_EXCEEDED: Requested {len(plan.nodes)} assets exceeds budget {self.max_scene_assets}."

        # 3. Construir SceneGraph
        sg = SceneGraph()
        for node in plan.nodes.values():
            sg.add_node(node)

        self.graphs[intent.scene_id] = sg
        self.plans[intent.scene_id] = plan

        return True, plan, f"Scene '{intent.scene_id}' planned with {len(plan.nodes)} nodes."

    def preview_scene(self, plan: ScenePlan) -> Tuple[bool, List[str], SceneSummary]:
        ok_spatial, errors = ProxyScene.validate_spatial_integrity(plan.nodes)
        summary = SceneSummary(
            scene_id=plan.scene_id,
            status=SceneStatus.PLANNED if ok_spatial else SceneStatus.DRAFT,
            total_assets=len(plan.nodes),
            landmarks=sum(1 for n in plan.nodes.values() if n.role == "LANDMARK"),
            structures=sum(1 for n in plan.nodes.values() if n.role in ["PRIMARY", "SECONDARY"]),
            triangles_estimate=len(plan.nodes) * 500,
            validation_score=1.0 if ok_spatial else 0.5
        )
        return ok_spatial, errors, summary

    def build_scene(
        self,
        plan: ScenePlan,
        provider: IBlenderProvider,
        fail_at_index: Optional[int] = None
    ) -> Tuple[int, bool, str]: # (built_count, is_idempotent, message)
        sg = self.graphs.get(plan.scene_id)
        if not sg:
            return 0, False, "SceneGraph not found."

        dirty_nodes = sg.get_dirty_nodes()
        if not dirty_nodes:
            return 0, True, "Idempotent: Scene is already clean (0 builds required)."

        nodes_to_process = list(dirty_nodes)
        if fail_at_index is not None and fail_at_index < len(nodes_to_process):
            nodes_to_process = nodes_to_process[:fail_at_index]

        built_count, built_ids = BatchSceneBuilder.build_node_batch(plan.scene_id, nodes_to_process, provider)

        # Actualizar estado dirty y guardar checkpoint
        built_set = set(built_ids)
        for nid in built_ids:
            sg.nodes[nid].dirty_state = NodeDirtyState.CLEAN

        self.checkpoint_manager.save_checkpoint(plan.scene_id, stage=BuildStage.PRIMARY_STRUCTURES, built_nodes=built_set)

        if fail_at_index is not None:
            return built_count, False, f"Simulated MCP failure at node index {fail_at_index}."

        return built_count, False, f"Scene '{plan.scene_id}' built {built_count} nodes successfully."

    def rebuild_node(
        self,
        scene_id: str,
        node_id: str,
        provider: IBlenderProvider
    ) -> Tuple[int, float, str]: # (rebuild_count, rebuild_ratio, message)
        sg = self.graphs.get(scene_id)
        if not sg or node_id not in sg.nodes:
            return 0, 0.0, "Node not found."

        affected_ids = sg.mark_dirty(node_id, propagate=True)
        nodes_to_rebuild = [sg.nodes[nid] for nid in affected_ids]

        rebuilt_count, _ = BatchSceneBuilder.build_node_batch(scene_id, nodes_to_rebuild, provider)
        for nid in affected_ids:
            sg.nodes[nid].dirty_state = NodeDirtyState.CLEAN

        total_nodes = len(sg.nodes)
        rebuild_ratio = round(rebuilt_count / max(1, total_nodes), 4)

        return rebuilt_count, rebuild_ratio, f"Rebuilt {rebuilt_count}/{total_nodes} nodes (Ratio: {rebuild_ratio})."

    def resume_scene_build(self, scene_id: str, plan: ScenePlan, provider: IBlenderProvider) -> Tuple[int, str]:
        sg = self.graphs.get(scene_id)
        if not sg:
            return 0, "SceneGraph not found."

        dirty_nodes = sg.get_dirty_nodes()
        if not dirty_nodes:
            return 0, "All nodes already built."

        built_count, built_ids = BatchSceneBuilder.build_node_batch(scene_id, dirty_nodes, provider)
        for nid in built_ids:
            sg.nodes[nid].dirty_state = NodeDirtyState.CLEAN

        return built_count, f"Resumed build: completed remaining {built_count} nodes."

    def reconcile_scene(self, scene_id: str, provider: IBlenderProvider) -> Dict[str, Any]:
        sg = self.graphs.get(scene_id)
        if not sg:
            return {"status": "NOT_FOUND"}
        return SceneReconciler.reconcile_scene(scene_id, sg, provider)
