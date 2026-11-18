import time
from typing import Dict, Any, List, Optional
from ..core.prompt_types import (
    IntentType, AssetClassType, ProvenanceType,
    CompilationStatus, ConflictSeverity
)
from ..core.prompt_schema import (
    CompiledSpecification, CompilationResult, ConversationContext,
    ClarificationRequest, RequirementConflict
)
from ..extractor.intent_requirement_extractor import IntentRequirementExtractor
from ..normalizer.unit_normalizer import UnitNormalizer

class SpecificationCompiler:
    @classmethod
    def compile_prompt(
        cls,
        text: str,
        context: Optional[ConversationContext] = None
    ) -> CompilationResult:
        context = context or ConversationContext()
        
        # 1. Extracción Inicial
        intent, asset_class = IntentRequirementExtractor.extract_intent_and_class(text)
        styles = IntentRequirementExtractor.extract_styles(text)
        materials = IntentRequirementExtractor.extract_materials(text)
        components, forbidden = IntentRequirementExtractor.extract_components_and_forbidden(text)
        gameplay_flags, derived = IntentRequirementExtractor.extract_gameplay(text)

        # 2. Detección de Conflictos Directos
        conflicts = IntentRequirementExtractor.detect_direct_conflicts(text, components, forbidden)
        if conflicts:
            return CompilationResult(
                status=CompilationStatus.CONFLICT,
                conflicts=conflicts,
                confidence=0.0,
                error_message=f"REQUIREMENT_CONFLICT: Detected {len(conflicts)} direct contradiction(s). Cannot compile specification."
            )

        # 3. Resolución de Modificaciones Relativas ("Hazlo más grande" / "igual que el anterior pero 20% más alto")
        dimensions: Dict[str, float] = {"width": 1.0, "height": 1.5, "depth": 1.0}
        provenance_map: Dict[str, ProvenanceType] = {}

        scale_mod = UnitNormalizer.parse_percentage_modifier(text)
        
        if "hazlo más grande" in text.lower() or "más alto" in text.lower() or "igual pero" in text.lower():
            if not context.active_asset_id:
                # No hay activo previo para referenciar -> Pedir Aclaración
                return CompilationResult(
                    status=CompilationStatus.CLARIFICATION_REQUIRED,
                    clarifications=[ClarificationRequest(
                        request_id="REQ_MISSING_REFERENCE",
                        question="No hay un activo activo previo seleccionado. ¿A qué activo deseas aplicar esta modificación?",
                        impact_category="REFERENCE",
                        suggested_options=["Seleccionar último barril", "Crear nuevo activo desde cero"]
                    )],
                    confidence=0.50,
                    error_message="CLARIFICATION_REQUIRED: Relative modification requested without an active reference asset."
                )
            else:
                # Modificación sobre activo existente
                asset_class = context.active_asset_class or asset_class
                if scale_mod:
                    dimensions["height"] = round(context.previous_parameters.get("height", 1.5) * scale_mod, 2)
                    provenance_map["height"] = ProvenanceType.USER_EXPLICIT

        # Si el usuario pide cambiar material pero no lo especifica
        if "cambia el material" in text.lower() and not materials:
            return CompilationResult(
                status=CompilationStatus.CLARIFICATION_REQUIRED,
                clarifications=[ClarificationRequest(
                    request_id="REQ_TARGET_MATERIAL",
                    question="¿Qué material deseas aplicar al activo (ej. madera oscura, piedra, metal)?",
                    impact_category="MATERIAL",
                    suggested_options=["Madera oscura", "Piedra rústica", "Metal forjado"]
                )],
                confidence=0.60,
                error_message="CLARIFICATION_REQUIRED: Material change requested without specifying target material."
            )

        # Mapeo de Provenance
        for comp in components:
            provenance_map[f"comp_{comp}"] = ProvenanceType.USER_EXPLICIT
        for d in derived:
            provenance_map[d] = ProvenanceType.DERIVED

        # Defaults seguros si no se especificaron detalles (evita alucinaciones de 17 detalles)
        if "bonito" in text.lower() and len(components) <= 1:
            provenance_map["aesthetic"] = ProvenanceType.DEFAULT

        spec_id = f"SPEC_{int(time.time()*1000)}"
        spec = CompiledSpecification(
            specification_id=spec_id,
            version="1.0.0",
            source_text=text,
            intent=intent,
            asset_class=asset_class,
            style=styles,
            components=components,
            dimensions=dimensions,
            materials=materials,
            gameplay_flags=gameplay_flags,
            derived_requirements=derived,
            forbidden_features=forbidden,
            provenance_map=provenance_map,
            confidence=0.95
        )

        return CompilationResult(
            status=CompilationStatus.SUCCESS,
            specification=spec,
            confidence=0.95
        )
