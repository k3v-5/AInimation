from typing import Dict, Any, Tuple
from ..core.msp_types import ComponentConstructionMethod, BasePrimitiveType

class ComponentClassifier:
    @classmethod
    def classify_component(cls, component_data: Dict[str, Any], prompt: str = "") -> Tuple[ComponentConstructionMethod, BasePrimitiveType]:
        sem_type = component_data.get("semantic_type", "BODY").upper()
        p_low = prompt.lower()
        
        # 1. Detección de patrones repetitivos / arrays (ej. aros, remaches, tejas, escalones)
        if "ring" in sem_type or "remache" in p_low or "repetitive" in p_low or "array" in p_low:
            return ComponentConstructionMethod.ARRAY_BASED, BasePrimitiveType.TORUS if "ring" in sem_type else BasePrimitiveType.CYLINDER

        # 2. Detección de armas / perfiles de espada
        if "blade" in sem_type or "hoja" in sem_type:
            return ComponentConstructionMethod.PROFILE_BASED, BasePrimitiveType.PROFILE

        if "guard" in sem_type or "guarda" in sem_type or "handle" in sem_type or "mango" in sem_type:
            return ComponentConstructionMethod.PARAMETRIC, BasePrimitiveType.CYLINDER

        # 3. Detección de cuerpos principales (barriles, cilindros, cajas)
        if "body" in sem_type or "cuerpo" in sem_type:
            if "barrel" in p_low or "barril" in p_low or "columna" in p_low:
                return ComponentConstructionMethod.PARAMETRIC, BasePrimitiveType.CYLINDER
            return ComponentConstructionMethod.PARAMETRIC, BasePrimitiveType.CUBE

        # 4. Elementos orgánicos / curvas
        if "curve" in p_low or "rope" in p_low or "cuerda" in p_low:
            return ComponentConstructionMethod.CURVE_BASED, BasePrimitiveType.CURVE

        # Default fallback
        return ComponentConstructionMethod.PRIMITIVE, BasePrimitiveType.CUBE
