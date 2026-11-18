from typing import Dict, Any, List, Optional
from ..core.reference_types import (
    ReferenceModality, CameraPerspective, ExtractedMaterialType,
    StyleArchetype, ConfidenceTier, VisualFeatureImportance
)
from ..core.reference_schema import (
    ImageReferenceInput, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ColorPalette, CameraEstimation,
    VisualRequirementItem, DecomposedReferenceReport
)
from ..engine.reference_decomposition_engine import ReferenceDecompositionEngine

class ReferenceAnalysisAPI:
    """
    Reference Analysis & Visual Decomposition Engine API (AOE v55)
    
    Regla Fundamental:
    LA REFERENCIA VISUAL DEJA DE SER UNA IMAGEN QUE LA IA "MIRA Y RECUERDA DE MEMORIA".
    SE CONVIERTE EN UNA ESPECIFICACIÓN MATEMÁTICA Y ESTRUCTURAL CON PESO REAL:
    SILUETA, PROPORCIONES, DESCOMPOSICIÓN DE PARTES, MATERIALES PBR, PALETAS DE COLOR Y ÁNGULO DE CÁMARA.
    """
    def __init__(self):
        pass

    def analyze_references(
        self,
        references: List[ImageReferenceInput],
        asset_class_hint: str = "PROP.BARREL",
        target_style: StyleArchetype = StyleArchetype.STYLIZED
    ) -> DecomposedReferenceReport:
        return ReferenceDecompositionEngine.decompose(
            references=references,
            asset_class_hint=asset_class_hint,
            target_style=target_style
        )
