"""
ImplementationRegistry manages concrete components executing capabilities.
UAF-81.2 Section 65, 68.
"""

from typing import List, Optional
from ...contracts.registry import BaseRegistry
from .implementation import ImplementationDescription, ExecutionBackend


class ImplementationRegistry(BaseRegistry[ImplementationDescription]):
    """
    Registry discovering concrete implementations for capabilities.
    """
    def __init__(self):
        super().__init__(name="ImplementationRegistry")
        self._init_standard_implementations()

    def _init_standard_implementations(self) -> None:
        standards = [
            ImplementationDescription(
                implementation_id="MockMeshGeneratorV1",
                capability_id="primitive_procedural_geometry",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="In-process Mock Mesh Generator",
            ),
            ImplementationDescription(
                implementation_id="ParametricAnatomyGeneratorV1",
                capability_id="parametric_anatomy",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Parametric Anatomy Generator",
            ),
            ImplementationDescription(
                implementation_id="OrganicSurfaceSculptV2",
                capability_id="organic_surface_generation",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Organic Surface Generator",
            ),
            ImplementationDescription(
                implementation_id="FacialMeshSynthesisV2",
                capability_id="advanced_facial_generation",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Advanced Facial Generator",
            ),
            ImplementationDescription(
                implementation_id="ClothGeometrySimV1",
                capability_id="cloth_geometry",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Cloth Geometry Generator",
            ),
            ImplementationDescription(
                implementation_id="HighDetailMicroSurfaceV1",
                capability_id="high_detail_surface",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="High Detail Surface Generator",
            ),
            ImplementationDescription(
                implementation_id="AdvancedTopologyOptimizerV1",
                capability_id="advanced_topology",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Advanced Topology Optimizer",
            ),

            ImplementationDescription(
                implementation_id="AutoRiggingEngineV1",
                capability_id="skeletal_rigging",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Skeletal Rig Generator",
            ),
            ImplementationDescription(
                implementation_id="BasicRiggingGeneratorV1",
                capability_id="basic_rigging",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Basic Biped Rig Generator",
            ),

            ImplementationDescription(
                implementation_id="ModularSocketMatcherV1",
                capability_id="modular_assembly",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Modular Assembly Component",
            ),
            ImplementationDescription(
                implementation_id="SocketAlignmentEngineV1",
                capability_id="socket_alignment",
                backend_type=ExecutionBackend.IN_PROCESS,
                name="Socket Alignment Engine",
            ),
        ]
        for imp in standards:
            self.register(imp.implementation_id, imp, overwrite=True)

    def find_for_capability(self, capability_id: str) -> List[ImplementationDescription]:
        return self.find(lambda imp: imp.capability_id == capability_id and imp.is_available)
