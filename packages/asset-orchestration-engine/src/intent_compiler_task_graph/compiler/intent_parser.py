import re
import time
from typing import Dict, Any, List, Optional
from ..core.intent_types import (
    RequirementType, RequirementPriority, RequirementSource,
    AmbiguitySeverity, AmbiguityCategory, PreflightStatus, ReferenceScopeType
)
from ..core.intent_schema import (
    UserRequest, Requirement, ExclusionItem, AmbiguityItem,
    ClarificationRequest, ReferenceTargetMask, CompiledIntent
)

class IntentParser:
    @staticmethod
    def parse_request(req: UserRequest) -> CompiledIntent:
        text = req.raw_text.lower()
        intent_id = f"INTENT_{int(time.time()*1000)}"
        reqs: List[Requirement] = []
        exclusions: List[ExclusionItem] = []
        ambiguities: List[AmbiguityItem] = []
        preferences: List[str] = []
        preflight = PreflightStatus.READY
        clarification: Optional[ClarificationRequest] = None

        # 1. Detección de Conflictos Bloqueantes (ej. "grande pero de máximo 3 metros")
        if "grande" in text and ("máximo 3 metros" in text or "max 3m" in text):
            return CompiledIntent(
                intent_id=intent_id,
                objective="CONFLICT",
                preflight_status=PreflightStatus.BLOCKING_CONFLICT,
                confidence=0.0
            )

        # 2. Detección de Conflictos Semánticos (ej. medieval + futurista)
        if "medieval" in text and "futurista" in text:
            amb = AmbiguityItem(
                ambiguity_id="AMB_STYLE_CONFLICT",
                term="medieval vs futurista",
                category=AmbiguityCategory.STYLE,
                severity=AmbiguitySeverity.HIGH,
                impact="Contradictory architectural style terms."
            )
            ambiguities.append(amb)
            preflight = PreflightStatus.NEEDS_CLARIFICATION
            clarification = ClarificationRequest(
                question_id="Q_STYLE_1",
                ambiguity=amb,
                options=["Medieval clásico (predeterminado)", "Estilo híbrido Sci-Fi/Medieval", "Futurista"],
                recommended_option="Medieval clásico (predeterminado)",
                blocking=False
            )

        # 3. Petición sin alcance ("Hazla como la imagen" sin especificar qué copiar)
        if ("como la imagen" in text or "parecida a la referencia" in text) and not req.references and "solamente" not in text and "estructura" not in text:
            amb = AmbiguityItem(
                ambiguity_id="AMB_REF_SCOPE",
                term="como la imagen",
                category=AmbiguityCategory.REFERENCE,
                severity=AmbiguitySeverity.BLOCKING,
                impact="Missing reference scope details."
            )
            ambiguities.append(amb)
            return CompiledIntent(
                intent_id=intent_id,
                objective="UNSPECIFIED_REFERENCE",
                ambiguities=ambiguities,
                preflight_status=PreflightStatus.NEEDS_CLARIFICATION,
                confidence=0.40,
                clarification_request=ClarificationRequest(
                    question_id="Q_REF_SCOPE",
                    ambiguity=amb,
                    options=["Copiar estructura y proporciones", "Inspirar solo materiales", "Copiar todo"],
                    recommended_option="Copiar estructura y proporciones",
                    blocking=True
                )
            )

        # 4. Extracción de Requisitos
        # Tipo de Activo
        asset_type = "HOUSE"
        if "torre" in text:
            asset_type = "TOWER"
        elif "castillo" in text:
            asset_type = "CASTLE"

        reqs.append(Requirement(
            req_id=f"REQ_{len(reqs)+1}",
            type=RequirementType.STRUCTURAL,
            priority=RequirementPriority.HARD,
            source=RequirementSource.USER_EXPLICIT,
            description=f"Asset type is {asset_type}",
            key="asset_type",
            value=asset_type
        ))

        # Estilo
        if "medieval" in text:
            reqs.append(Requirement(
                req_id=f"REQ_{len(reqs)+1}",
                type=RequirementType.STYLE,
                priority=RequirementPriority.HARD,
                source=RequirementSource.USER_EXPLICIT,
                description="Medieval architectural style",
                key="style",
                value="MEDIEVAL"
            ))

        # Ventanas
        win_match = re.search(r'(\d+)\s+ventanas?', text)
        if win_match:
            count = int(win_match.group(1))
            reqs.append(Requirement(
                req_id=f"REQ_{len(reqs)+1}",
                type=RequirementType.STRUCTURAL,
                priority=RequirementPriority.HARD,
                source=RequirementSource.USER_EXPLICIT,
                description=f"Exact window count: {count}",
                key="window_count",
                value=count
            ))

        # Puertas
        if "puerta" in text or "una puerta" in text:
            reqs.append(Requirement(
                req_id=f"REQ_{len(reqs)+1}",
                type=RequirementType.STRUCTURAL,
                priority=RequirementPriority.HARD,
                source=RequirementSource.USER_EXPLICIT,
                description="Exact door count: 1",
                key="door_count",
                value=1
            ))

        # Techo
        if "tejado inclinado" in text or "techo inclinado" in text or "techo" in text:
            reqs.append(Requirement(
                req_id=f"REQ_{len(reqs)+1}",
                type=RequirementType.GEOMETRIC,
                priority=RequirementPriority.HARD,
                source=RequirementSource.USER_EXPLICIT,
                description="Pitched/Gable roof geometry",
                key="roof_type",
                value="PITCHED"
            ))

        # Materiales
        mats = []
        if "piedra" in text:
            mats.append("STONE")
        if "madera" in text:
            mats.append("TIMBER")
        if mats:
            reqs.append(Requirement(
                req_id=f"REQ_{len(reqs)+1}",
                type=RequirementType.MATERIAL,
                priority=RequirementPriority.HARD,
                source=RequirementSource.USER_EXPLICIT,
                description=f"PBR materials: {mats}",
                key="materials",
                value=mats
            ))

        # Exclusiones
        exclusions.append(ExclusionItem(
            exclusion_id="EXCL_MODERN",
            description="Prohibit modern/futuristic architecture",
            prohibited_terms=["modern_windows", "steel_frame", "neon", "concrete_modern"]
        ))

        # Máscara de referencia (Target vs Context vs Ignore)
        mask = ReferenceTargetMask(
            target=["building", "house", "structure"],
            context=["trees", "vegetation", "ground"],
            ignore=["sky", "clouds", "lighting"],
            scope=ReferenceScopeType.COPY_STRUCTURE
        )

        return CompiledIntent(
            intent_id=intent_id,
            objective=f"CREATE_{asset_type}",
            requirements=reqs,
            exclusions=exclusions,
            preferences=preferences,
            ambiguities=ambiguities,
            target_mask=mask,
            preflight_status=preflight,
            confidence=0.95,
            clarification_request=clarification
        )
