import time
from typing import Dict, Any, List, Optional
from ..core.twin_types import (
    GraphNodeType, GraphRelationType, ReconciliationState,
    ComponentLifecycleState, AssetLifecycleState, ImpactLevel, DiffType
)
from ..core.twin_schema import (
    AssetIdentity, ComponentIdentity, SemanticComponentNode,
    SemanticRelationship, SemanticAnchor, SemanticSocket,
    AssetSnapshot, SemanticDiff, RegenerationBoundary
)
from ..graph.semantic_asset_graph import SemanticAssetGraph
from ..engine.digital_twin_reconciler import DigitalTwinReconciler
from ..engine.impact_analyzer import AssetImpactAnalyzer
from ..engine.semantic_resolver import SemanticResolver
from ..engine.asset_diff_engine import AssetDiffEngine

class SemanticDigitalTwinAPI:
    """
    Semantic Asset Graph & Digital Twin API (AOE v54)
    
    Regla Fundamental:
    EL SISTEMA DEJA DE TRATAR UN MODELO COMO "UN MONTÓN DE OBJETOS DE BLENDER"
    Y LO TRATA COMO UN GRAFO SEMÁNTICO CON IDENTIDADES ESTABLES (semantic_id),
    LÍMITES DE REGENERACIÓN MÍNIMOS, RESOLUCIÓN NATURAL Y RECONCILIACIÓN CON BLENDER.
    """
    def __init__(self):
        self._graphs: Dict[str, SemanticAssetGraph] = {}

    def get_or_create_graph(self, asset_id: str) -> SemanticAssetGraph:
        if asset_id not in self._graphs:
            self._graphs[asset_id] = SemanticAssetGraph(asset_id)
        return self._graphs[asset_id]

    def register_component(
        self,
        asset_id: str,
        component_id: str,
        semantic_id: str,
        semantic_type: str,
        blender_object_name: str,
        transform: Optional[Dict[str, Any]] = None,
        material_name: str = "DEFAULT_MATERIAL",
        is_locked: bool = False
    ) -> SemanticComponentNode:
        graph = self.get_or_create_graph(asset_id)
        node = SemanticComponentNode(
            component_id=component_id,
            semantic_id=semantic_id,
            semantic_type=semantic_type,
            blender_object_name=blender_object_name,
            transform=transform or {"location": (0,0,0), "rotation": (0,0,0), "scale": (1,1,1)},
            material_name=material_name,
            is_locked=is_locked
        )
        graph.add_node(node)
        return node

    def add_dependency(self, asset_id: str, source_component_id: str, target_component_id: str):
        graph = self.get_or_create_graph(asset_id)
        graph.add_relationship(source_component_id, target_component_id, GraphRelationType.DEPENDS_ON)

    def calculate_regeneration_boundary(
        self,
        asset_id: str,
        target_component_id: str,
        parameter_modified: Optional[str] = None
    ) -> RegenerationBoundary:
        graph = self.get_or_create_graph(asset_id)
        return AssetImpactAnalyzer.calculate_regeneration_boundary(graph, target_component_id, parameter_modified)

    def resolve_natural_query(self, asset_id: str, query_text: str) -> Optional[str]:
        graph = self.get_or_create_graph(asset_id)
        return SemanticResolver.resolve_natural_reference(graph, query_text)

    def reconcile_with_blender(
        self,
        asset_id: str,
        blender_scene_objects: Dict[str, Dict[str, Any]],
        twin_modified_components: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        graph = self.get_or_create_graph(asset_id)
        return DigitalTwinReconciler.reconcile(graph, blender_scene_objects, twin_modified_components)

    def create_snapshot(self, asset_id: str, snapshot_id: str) -> AssetSnapshot:
        graph = self.get_or_create_graph(asset_id)
        return graph.create_snapshot(snapshot_id)

    def compute_diff(self, snapshot_a: AssetSnapshot, snapshot_b: AssetSnapshot) -> List[SemanticDiff]:
        return AssetDiffEngine.compute_diff(snapshot_a, snapshot_b)
