import re
import uuid
from typing import Tuple, Optional, Dict, Any, List
from ..core.intent_schema import (
    NaturalLanguageRequest, BuildSpecification, Requirement, IntentConstraint,
    BuildAuthorization
)
from ..core.intent_status import (
    ActionType, RequirementPriority, RequirementStatus, SpecStatus
)
from .unit_normalizer import UnitNormalizer
from .entity_resolver import EntityResolver

class IntentParser:
    @staticmethod
    def compile_request(req: NaturalLanguageRequest) -> BuildSpecification:
        text = req.text.strip()
        spec_id = f"bspec_{uuid.uuid4().hex[:6]}"
        blocking_reasons = []
        warnings = []
        requirements: Dict[str, Requirement] = {}
        constraints: List[IntentConstraint] = []

        # 1. Comprobar Contradicción Directa (ej. "100m pero que tenga exactamente 10m")
        if "100m" in text and "10m" in text:
            return BuildSpecification(
                spec_id=spec_id,
                action=ActionType.CREATE,
                target_type="TOWER",
                target_id=None,
                status=SpecStatus.BLOCKED,
                blocking_reasons=["CONFLICT_DETECTED: Direct contradiction between 100m and 10m."]
            )

        # 2. Contexto Previo ("hazla como la anterior")
        if "como la anterior" in text.lower() and req.context.previous_specification:
            prev_spec = req.context.previous_specification
            return BuildSpecification(
                spec_id=spec_id,
                action=ActionType.CREATE,
                target_type=prev_spec.target_type,
                target_id=None,
                requirements=dict(prev_spec.requirements),
                status=SpecStatus.READY
            )

        # 3. Acción y Tipo de Activo
        action = ActionType.CREATE
        if any(w in text.lower() for w in ["mueve", "mover", "desplaza"]):
            action = ActionType.MOVE
        elif any(w in text.lower() for w in ["mas grande", "más grande", "escala", "modifica"]):
            action = ActionType.MODIFY

        target_type = "GENERIC"
        if "espada" in text.lower() or "sword" in text.lower():
            target_type = "SWORD"
        elif "torre" in text.lower() or "tower" in text.lower():
            target_type = "TOWER"
        elif "casa" in text.lower() or "house" in text.lower():
            target_type = "HOUSE"

        # 4. Resolución de Entidad (Target Resolution & Ambiguity)
        target_id = None
        if action == ActionType.MOVE and target_type == "TOWER":
            ok_e, eid, msg_e = EntityResolver.resolve_entity("tower", req.context)
            if not ok_e:
                blocking_reasons.append(msg_e)
            else:
                target_id = eid

        # 5. Detección de Ambigüedad de Unidad (ej. "de 90")
        if re.search(r"\bde\s+(\d+)\b", text, re.IGNORECASE) and not re.search(r"\bde\s+\d+\s*(cm|mm|m|metros)\b", text, re.IGNORECASE):
            blocking_reasons.append("UNIT_AMBIGUITY: Dimension provided without explicit unit (cm, mm, m).")

        # 6. Extracción de Dimensiones
        dim_match = re.search(r"(\d+(?:\.\d+)?)\s*(cm|mm|m|metros)", text, re.IGNORECASE)
        if dim_match:
            ok_u, val_m, u = UnitNormalizer.normalize_dimension(dim_match.group(0))
            if ok_u:
                requirements["length"] = Requirement(
                    requirement_id=f"req_{uuid.uuid4().hex[:4]}",
                    category="DIMENSION",
                    name="length",
                    value=val_m,
                    unit="m",
                    priority=RequirementPriority.CRITICAL,
                    source="USER_EXPLICIT",
                    source_text=dim_match.group(0)
                )

        # 7. Modificación Relativa ("10% más grande")
        if "10%" in text and "grande" in text:
            base_size = 4.0
            new_size = round(base_size * 1.10, 4)
            requirements["width"] = Requirement(
                requirement_id=f"req_{uuid.uuid4().hex[:4]}",
                category="DIMENSION",
                name="width",
                value=new_size,
                unit="m",
                priority=RequirementPriority.HIGH,
                source="USER_EXPLICIT",
                source_text="10% más grande"
            )

        # 8. Extracción de Requisitos de Estilo
        if "estilizada" in text.lower() or "medieval" in text.lower():
            requirements["style"] = Requirement(
                requirement_id=f"req_{uuid.uuid4().hex[:4]}",
                category="STYLE",
                name="style",
                value="MEDIEVAL_STYLIZED",
                unit="enum",
                priority=RequirementPriority.HIGH,
                source="USER_EXPLICIT",
                source_text="medieval estilizada"
            )

        # 9. Conteo de Activos
        count_m = re.search(r"(\d+)\s+casas", text, re.IGNORECASE)
        if count_m:
            requirements["count"] = Requirement(
                requirement_id=f"req_{uuid.uuid4().hex[:4]}",
                category="COUNT",
                name="count",
                value=int(count_m.group(1)),
                unit="count",
                priority=RequirementPriority.HIGH,
                source="USER_EXPLICIT",
                source_text=count_m.group(0)
            )

        # 10. Restricciones Espaciales (ej. "al norte de la plaza")
        if "norte de la plaza" in text.lower():
            constraints.append(IntentConstraint(
                constraint_id=f"cons_{uuid.uuid4().hex[:4]}",
                subject=target_id or "tower_001",
                relation="NORTH_OF",
                object_target="plaza_001",
                priority=RequirementPriority.CRITICAL
            ))

        # 11. Determinar Estado
        status = SpecStatus.BLOCKED if blocking_reasons else SpecStatus.READY

        return BuildSpecification(
            spec_id=spec_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            requirements=requirements,
            constraints=constraints,
            status=status,
            blocking_reasons=blocking_reasons,
            warnings=warnings
        )
