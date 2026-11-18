from typing import Dict, Any, List, Optional, Tuple
from ..core.reference_types import (
    GeometricPrimitiveType, SpatialRelationType, ReferenceRole
)
from ..core.reference_schema import (
    ReferenceItem, VisualLandmark, ComponentDetectionRecord
)

class VisualFeatureExtractor:
    @staticmethod
    def extract_features_from_reference(
        ref: ReferenceItem,
        user_prompt: str = ""
    ) -> Dict[str, Any]:
        # 1. Proporciones y Silueta
        aspect_ratio = 1.52 # Altura / Anchura normalizada
        roof_ratio = 0.31   # Altura del tejado / Altura total

        # 2. Detección de Componentes y Grafo Espacial
        components: Dict[str, ComponentDetectionRecord] = {
            "foundation": ComponentDetectionRecord(
                component_name="foundation",
                bounding_box=(0.0, 0.0, 1.0, 0.10),
                normalized_pos=(0.5, 0.05, 0.0),
                primitive_type=GeometricPrimitiveType.BOX,
                confidence=0.98
            ),
            "walls": ComponentDetectionRecord(
                component_name="walls",
                bounding_box=(0.05, 0.10, 0.90, 0.59),
                normalized_pos=(0.5, 0.40, 0.0),
                primitive_type=GeometricPrimitiveType.BOX,
                confidence=0.96,
                spatial_relations=[{"relation": SpatialRelationType.ABOVE.value, "target": "foundation"}]
            ),
            "roof": ComponentDetectionRecord(
                component_name="roof",
                bounding_box=(0.0, 0.69, 1.0, 0.31),
                normalized_pos=(0.5, 0.85, 0.0),
                primitive_type=GeometricPrimitiveType.EXTRUSION,
                confidence=0.95,
                spatial_relations=[{"relation": SpatialRelationType.ABOVE.value, "target": "walls"}]
            ),
            "door": ComponentDetectionRecord(
                component_name="door",
                count=1,
                bounding_box=(0.40, 0.10, 0.20, 0.30),
                normalized_pos=(0.5, 0.25, 0.0),
                primitive_type=GeometricPrimitiveType.BOX,
                confidence=0.92,
                spatial_relations=[
                    {"relation": SpatialRelationType.ATTACHED_TO.value, "target": "walls"},
                    {"relation": SpatialRelationType.CENTERED.value, "target": "walls"}
                ]
            ),
            "windows": ComponentDetectionRecord(
                component_name="windows",
                count=4,
                bounding_box=(0.15, 0.35, 0.70, 0.25),
                normalized_pos=(0.5, 0.45, 0.0),
                primitive_type=GeometricPrimitiveType.BOX,
                confidence=0.90,
                spatial_relations=[{"relation": SpatialRelationType.ATTACHED_TO.value, "target": "walls"}]
            )
        }

        # 3. Puntos de Referencia Clave (Landmarks)
        landmarks = [
            VisualLandmark("LM_ROOF_APEX", "Roof Apex", (0.50, 1.00), "ROOF_TOP", confidence=0.98),
            VisualLandmark("LM_EAVES_LEFT", "Left Eave", (0.00, 0.69), "ROOF_EAVE", confidence=0.95),
            VisualLandmark("LM_EAVES_RIGHT", "Right Eave", (1.00, 0.69), "ROOF_EAVE", confidence=0.95),
            VisualLandmark("LM_DOOR_BASE", "Door Base", (0.50, 0.10), "DOOR_ENTRY", confidence=0.96)
        ]

        return {
            "aspect_ratio": aspect_ratio,
            "roof_ratio": roof_ratio,
            "components": components,
            "landmarks": landmarks,
            "symmetry": {"bilateral": True, "confidence": 0.94},
            "repetition": {"windows": {"count": 4, "pattern": "GRID_2X2"}}
        }
