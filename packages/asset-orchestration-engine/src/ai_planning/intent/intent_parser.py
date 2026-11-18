from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class PlanningIntentType(str, Enum):
    MAKE_PICKABLE = "MAKE_PICKABLE"
    MAKE_EQUIPPABLE = "MAKE_EQUIPPABLE"
    MODIFY_PROPERTY = "MODIFY_PROPERTY"
    MODIFY_SCALE = "MODIFY_SCALE"
    MODIFY_MATERIAL = "MODIFY_MATERIAL"
    MOVE = "MOVE"
    PLACE_ON = "PLACE_ON"
    DELETE = "DELETE"
    CREATE_VARIANT = "CREATE_VARIANT"
    INSPECT = "INSPECT"

@dataclass
class ParsedIntent:
    intent_type: PlanningIntentType
    target_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    desired_state: Dict[str, Any] = field(default_factory=dict)

class AdvancedIntentParser:
    @staticmethod
    def parse_user_request(text: str, context_target: Optional[str] = None) -> List[ParsedIntent]:
        t = text.lower()
        intents: List[ParsedIntent] = []
        target = context_target

        # 1. Comportamientos Gameplay
        if "recoger" in t or "pick" in t:
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.MAKE_PICKABLE,
                target_id=target,
                desired_state={"pickable": True}
            ))
        if "equipar" in t or "equip" in t:
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.MAKE_EQUIPPABLE,
                target_id=target,
                desired_state={"equippable": True}
            ))

        # 2. Modificación de Datos (Daño, Atributos)
        if "daño" in t or "damage" in t:
            # Extraer número si existe
            words = t.replace(".", "").split()
            dmg_val = 40.0
            for w in words:
                if w.isdigit():
                    dmg_val = float(w)
                    break
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.MODIFY_PROPERTY,
                target_id=target,
                parameters={"property": "damage", "value": dmg_val},
                desired_state={"damage": dmg_val}
            ))

        # 3. Escala y Dimensiones
        if "grande" in t or "scale" in t or "más larga" in t:
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.MODIFY_SCALE,
                target_id=target,
                parameters={"scale_factor": 1.2},
                desired_state={"scale": 1.2}
            ))

        # 4. Material y Color
        if "roja" in t or "rojo" in t or "material" in t:
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.MODIFY_MATERIAL,
                target_id=target,
                parameters={"base_color": "#FF0000"},
                desired_state={"material_color": "#FF0000"}
            ))

        # 5. Colocación Espacial
        if "mesa" in t or "sobre" in t or "place" in t:
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.PLACE_ON,
                target_id=target,
                parameters={"reference_target": "table_001", "relation": "ON_TOP_OF"}
            ))

        # 6. Borrado Destructivo
        if "elimina" in t or "delete" in t or "borrar" in t:
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.DELETE,
                target_id=target,
                parameters={"scope": "all" if "todas" in t else "target"}
            ))

        # 7. Creación de Variantes
        if "variante" in t or "variant" in t:
            intents.append(ParsedIntent(
                intent_type=PlanningIntentType.CREATE_VARIANT,
                target_id=target,
                parameters={"source_asset": target}
            ))

        return intents
