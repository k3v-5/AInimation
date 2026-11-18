import time
from typing import Dict, Any, List
from ..nodes.graph_node import GraphNode
from ..nodes.node_types import NodeType
from ..edges.graph_edge import GraphEdge
from ..edges.edge_types import RelationshipType
from ..storage.graph_store import ProjectKnowledgeGraphStore

class BlenderGraphExtractor:
    """
    Extracts structural scenes, collections, objects, meshes and materials
    from Blender data and converts them into Knowledge Graph nodes and edges.
    """
    def __init__(self, store: ProjectKnowledgeGraphStore):
        self.store = store

    def ingest_blender_scene_data(
        self,
        blend_file_path: str,
        scene_data: Dict[str, Any],
        semantic_asset_id: str,
        job_id: str = "JOB_INGEST",
        agent_id: str = "agent.blender.execution"
    ) -> List[str]:
        created_node_ids = []

        # 1. Blend File Node
        blend_node_id = f"BLEND_{blend_file_path.replace(':', '').replace('/', '_').replace('\\', '_')}"
        blend_node = GraphNode(
            node_id=blend_node_id,
            node_type=NodeType.BLEND_FILE,
            source="BLENDER",
            metadata={"path": blend_file_path}
        )
        self.store.add_node(blend_node)
        created_node_ids.append(blend_node_id)

        # 2. Primary Asset Node
        asset_node_id = f"ASSET_{semantic_asset_id}"
        asset_node = self.store.get_node(asset_node_id)
        if not asset_node:
            asset_node = GraphNode(
                node_id=asset_node_id,
                node_type=NodeType.ASSET,
                semantic_id=semantic_asset_id,
                source="AOE",
                metadata={"status": "ACTIVE"}
            )
            self.store.add_node(asset_node)
            created_node_ids.append(asset_node_id)

        # 3. Ingest Objects and Materials
        for obj in scene_data.get("objects", []):
            obj_name = obj.get("name", "Unknown_Object")
            obj_node_id = f"OBJ_{obj_name}"
            obj_node = GraphNode(
                node_id=obj_node_id,
                node_type=NodeType.BLENDER_OBJECT,
                semantic_id=f"{semantic_asset_id}.{obj_name.lower()}",
                source="BLENDER",
                metadata=obj
            )
            self.store.add_node(obj_node)
            created_node_ids.append(obj_node_id)

            # Edge: Asset CONTAINS Object
            self.store.add_edge(GraphEdge(
                edge_id=f"EDGE_{asset_node_id}_CONTAINS_{obj_node_id}",
                source_node=asset_node_id,
                target_node=obj_node_id,
                relationship_type=RelationshipType.CONTAINS,
                job_id=job_id, agent_id=agent_id
            ))

            # Ingest Material assignments
            for mat_name in obj.get("materials", []):
                mat_node_id = f"MAT_{mat_name}"
                if not self.store.get_node(mat_node_id):
                    mat_node = GraphNode(
                        node_id=mat_node_id,
                        node_type=NodeType.MATERIAL,
                        source="BLENDER",
                        metadata={"material_name": mat_name}
                    )
                    self.store.add_node(mat_node)
                    created_node_ids.append(mat_node_id)

                # Edge: Object USES Material
                self.store.add_edge(GraphEdge(
                    edge_id=f"EDGE_{obj_node_id}_USES_{mat_node_id}",
                    source_node=obj_node_id,
                    target_node=mat_node_id,
                    relationship_type=RelationshipType.USES,
                    job_id=job_id, agent_id=agent_id
                ))

                # Edge: Asset USES Material
                self.store.add_edge(GraphEdge(
                    edge_id=f"EDGE_{asset_node_id}_USES_{mat_node_id}",
                    source_node=asset_node_id,
                    target_node=mat_node_id,
                    relationship_type=RelationshipType.USES,
                    job_id=job_id, agent_id=agent_id
                ))

        return created_node_ids
