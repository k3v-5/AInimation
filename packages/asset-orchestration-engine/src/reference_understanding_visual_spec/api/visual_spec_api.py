from typing import Dict, Any, List, Optional
from ..core.reference_types import (
    ReferenceType, ReferenceRole, GeometricPrimitiveType,
    SpatialRelationType, UncertaintyType, SpecificationPriority,
    TargetProfileType, DetailTreatmentType
)
from ..core.reference_schema import (
    ReferenceItem, VisualLandmark, ComponentDetectionRecord,
    ProportionConstraint, UncertaintyItem, FeatureParameterAttribution,
    VisualSpecification, StructuralSpecification, VisualTargetProfile
)
from ..spec.specification_compiler import SpecificationCompiler
from ..spec.parameter_influence_mapper import ParameterInfluenceMapper

class VisualSpecificationAPI:
    """
    Reference Understanding & Visual Specification API (AOE v45)
    
    Regla Fundamental:
    UNA IMAGEN DE REFERENCIA NUNCA SE TRANSFORMA DIRECTAMENTE EN GEOMETRÍA A CIEGAS.
    SE CONVIERTE EN UNA ESPECIFICACIÓN VISUAL Y ESTRUCTURAL CON TOLERANCIAS FORMALES,
    RESTRICCIONES DE GAMEPLAY Y ATRIBUCIÓN DE PARÁMETROS PARA CRITIC Y GENERADORES.
    """
    def __init__(self):
        self.compiler = SpecificationCompiler()

    def create_reference_item(
        self,
        ref_id: str,
        uri: str,
        role: ReferenceRole = ReferenceRole.PRIMARY,
        ref_type: ReferenceType = ReferenceType.IMAGE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReferenceItem:
        return ReferenceItem(
            reference_id=ref_id,
            uri=uri,
            ref_type=ref_type,
            role=role,
            metadata=metadata or {}
        )

    def analyze_references_to_visual_spec(
        self,
        references: List[ReferenceItem],
        archetype_id: str = "MEDIEVAL_HOUSE",
        user_prompt: str = ""
    ) -> VisualSpecification:
        return self.compiler.compile_visual_specification(references, archetype_id, user_prompt)

    def compile_structural_specification(
        self,
        vspec: VisualSpecification,
        user_overrides: Optional[Dict[str, Any]] = None
    ) -> StructuralSpecification:
        return self.compiler.translate_to_structural_specification(vspec, user_overrides)

    def get_parameter_attribution(self, feature_name: str) -> Optional[FeatureParameterAttribution]:
        return ParameterInfluenceMapper.get_attribution(feature_name)
