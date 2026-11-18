from typing import Dict, List, Optional
from ..core.intent_types import TaskCriticality, MilestoneType
from ..core.intent_schema import CompiledIntent, TaskGraphNode, TaskGraphDAG

class TaskGraphBuilder:
    @staticmethod
    def build_dag(intent: CompiledIntent) -> TaskGraphDAG:
        nodes: Dict[str, TaskGraphNode] = {}

        # 1. Dimensiones y Huella
        nodes["T_DIMENSIONS"] = TaskGraphNode(
            node_id="T_DIMENSIONS",
            name="Establish Asset Dimensions",
            requires=[],
            produces=["footprint"],
            consumes=[],
            required_capabilities=["geometry_generation"],
            cost=1,
            milestone=MilestoneType.FOUNDATION_READY
        )

        # 2. Muros
        nodes["T_WALLS"] = TaskGraphNode(
            node_id="T_WALLS",
            name="Build Wall Geometry",
            requires=["T_DIMENSIONS"],
            produces=["walls"],
            consumes=["footprint"],
            required_capabilities=["geometry_generation", "blender_mesh_creation"],
            cost=3,
            milestone=MilestoneType.STRUCTURE_READY
        )

        # 3. Techo
        nodes["T_ROOF"] = TaskGraphNode(
            node_id="T_ROOF",
            name="Build Roof Geometry",
            requires=["T_WALLS"],
            produces=["roof"],
            consumes=["walls"],
            required_capabilities=["geometry_generation", "blender_mesh_creation"],
            cost=3,
            milestone=MilestoneType.ROOF_READY
        )

        # 4. Puertas y Ventanas
        nodes["T_OPENINGS"] = TaskGraphNode(
            node_id="T_OPENINGS",
            name="Build Doors and Windows",
            requires=["T_WALLS"],
            produces=["windows", "doors"],
            consumes=["walls"],
            required_capabilities=["geometry_generation", "component_placement"],
            cost=2,
            milestone=MilestoneType.COMPONENTS_READY
        )

        # 5. Materiales PBR
        nodes["T_MATERIALS"] = TaskGraphNode(
            node_id="T_MATERIALS",
            name="Assign PBR Materials",
            requires=["T_ROOF", "T_OPENINGS"],
            produces=["materials_applied"],
            consumes=["walls", "roof", "windows", "doors"],
            required_capabilities=["material_assignment"],
            cost=2,
            milestone=MilestoneType.MATERIALS_READY
        )

        # 6. Validación Final
        nodes["T_VALIDATE"] = TaskGraphNode(
            node_id="T_VALIDATE",
            name="Validate Geometric & Visual Quality",
            requires=["T_MATERIALS"],
            produces=["validated_asset"],
            consumes=["materials_applied"],
            required_capabilities=["quality_validation"],
            cost=1,
            milestone=MilestoneType.ASSET_READY
        )

        milestones = [
            MilestoneType.FOUNDATION_READY,
            MilestoneType.STRUCTURE_READY,
            MilestoneType.ROOF_READY,
            MilestoneType.COMPONENTS_READY,
            MilestoneType.MATERIALS_READY,
            MilestoneType.ASSET_READY
        ]

        return TaskGraphDAG(
            graph_id=f"DAG_{intent.intent_id}",
            nodes=nodes,
            milestones=milestones
        )
