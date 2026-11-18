import re
from typing import Dict, Any, Optional, Union, List, Tuple
from .intent_types import IntentType, ModifierType, NormalizedIntent
from ..specification.normalizer import UnitNormalizer
from ..specification.asset_schema import DimensionsSpec

class IntentParser:
    UNIT_PATTERN = r'([0-9]+(?:\.[0-9]+)?)\s*(mm|cm|m|meter|meters|in|inch|inches|ft|foot|feet|uu)?'

    @classmethod
    def parse_dimension_value(cls, text: str) -> Optional[float]:
        match = re.search(cls.UNIT_PATTERN, text.lower())
        if match:
            num = float(match.group(1))
            unit = match.group(2) or "meters"
            norm = UnitNormalizer.normalize_dimensions(DimensionsSpec(height=num, width=num, depth=num, unit=unit))
            return norm.height
        return None

    @classmethod
    def parse_intent(cls, input_data: Union[str, Dict[str, Any]], active_asset_id: Optional[str] = None) -> NormalizedIntent:
        if isinstance(input_data, dict):
            return cls._parse_dict_intent(input_data)
        elif isinstance(input_data, str):
            return cls._parse_nl_intent(input_data, active_asset_id)
        return NormalizedIntent(intent_type=IntentType.UNKNOWN, confidence=0.0, raw_text=str(input_data))

    @classmethod
    def _parse_dict_intent(cls, data: Dict[str, Any]) -> NormalizedIntent:
        itype_str = data.get("intent", data.get("type", "UNKNOWN")).upper()
        try:
            itype = IntentType(itype_str)
        except ValueError:
            itype = IntentType.UNKNOWN

        mod_str = data.get("modifier_type", data.get("operation_type", "SET")).upper()
        try:
            mod_type = ModifierType(mod_str)
        except ValueError:
            mod_type = ModifierType.SET

        return NormalizedIntent(
            intent_type=itype,
            confidence=float(data.get("confidence", 1.0)),
            asset_id=data.get("asset_id", data.get("asset")),
            target_component=data.get("target_component", data.get("target")),
            modifier_type=mod_type,
            property_name=data.get("property", "dimensions"),
            dimension_axis=data.get("dimension", data.get("axis", "height")),
            value=data.get("value"),
            parameters=data.get("parameters", data.get("asset", {})),
            raw_text=data.get("raw_text", "")
        )

    @classmethod
    def _parse_nl_intent(cls, text: str, active_asset_id: Optional[str] = None) -> NormalizedIntent:
        t = text.lower().strip()
        raw_text = text

        # 1. Intent: CREATE_ASSET
        if any(w in t for w in ["crea ", "crear ", "create ", "construye ", "genera ", "new "]):
            # Detectar categoría / tipo
            asset_type = "prop"
            if "espada" in t or "sword" in t: asset_type = "sword"
            elif "cubo" in t or "cube" in t: asset_type = "cube"
            elif "barril" in t or "barrel" in t: asset_type = "barrel"
            elif "escudo" in t or "shield" in t: asset_type = "shield"

            dim_val = cls.parse_dimension_value(t) or 1.0

            return NormalizedIntent(
                intent_type=IntentType.CREATE_ASSET,
                confidence=0.95,
                asset_id=active_asset_id or f"{asset_type}_001",
                value=dim_val,
                raw_text=raw_text,
                parameters={"type": asset_type, "raw": text, "dimension": dim_val}
            )

        # 2. Intent: DELETE
        if any(w in t for w in ["elimina ", "eliminar ", "borra ", "borrar ", "delete ", "remove "]):
            target = None
            for w in ["mango", "handle", "guarda", "guard", "hoja", "blade", "espada", "sword"]:
                if w in t: target = w; break
            return NormalizedIntent(
                intent_type=IntentType.DELETE_ASSET if "espada" in t or "asset" in t else IntentType.MODIFY_ASSET,
                confidence=0.90,
                asset_id=active_asset_id,
                target_component=target,
                modifier_type=ModifierType.SET,
                parameters={"action": "delete"},
                raw_text=raw_text
            )

        # 3. Intent: INSPECT
        if any(w in t for w in ["inspecciona", "inspect", "muestra", "consultar"]):
            return NormalizedIntent(
                intent_type=IntentType.INSPECT_ASSET,
                confidence=0.95,
                asset_id=active_asset_id,
                raw_text=raw_text
            )

        # 4. Intent: VALIDATE
        if any(w in t for w in ["valida", "validate", "comprueba", "check"]):
            return NormalizedIntent(
                intent_type=IntentType.VALIDATE_ASSET,
                confidence=0.95,
                asset_id=active_asset_id,
                raw_text=raw_text
            )

        # 5. Intent: MODIFY_ASSET (Cálculo de Modificador)
        # 5.1 MULTIPLY (% porcentaje)
        pct_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%', t)
        if pct_match:
            pct = float(pct_match.group(1))
            factor = 1.0 + (pct / 100.0) if ("mas" in t or "more" in t or "alarga" in t or "grande" in t) else (pct / 100.0)
            target = cls._extract_target_word(t)
            return NormalizedIntent(
                intent_type=IntentType.MODIFY_ASSET,
                confidence=0.95,
                asset_id=active_asset_id,
                target_component=target,
                modifier_type=ModifierType.MULTIPLY,
                property_name="dimensions",
                dimension_axis="height" if any(w in t for w in ["larga", "largo", "alarga", "longitud", "alto"]) else "all",
                value=factor,
                raw_text=raw_text
            )

        # 5.2 INCREMENT ("agrega 20cm", "alarga 10cm", "hazlo 10cm mas ancho")
        if any(w in t for w in ["agrega", "suma", "anade", "alarga", "mas larga", "mas largo", "mas ancho", "mas alto", "aumenta"]):
            val = cls.parse_dimension_value(t)
            target = cls._extract_target_word(t)
            axis = "width" if "ancho" in t else ("depth" if ("grosor" in t or "profundo" in t) else "height")
            return NormalizedIntent(
                intent_type=IntentType.MODIFY_ASSET,
                confidence=0.95,
                asset_id=active_asset_id,
                target_component=target,
                modifier_type=ModifierType.INCREMENT,
                property_name="dimensions",
                dimension_axis=axis,
                value=val if val is not None else 0.10,
                raw_text=raw_text
            )

        # 5.3 SET ("hazlo de 2m", "dejalo en 2m", "fijar a 85cm")
        if any(w in t for w in ["hazlo de", "dejalo en", "ajusta a", "ponlo en", "mide", "set "]):
            val = cls.parse_dimension_value(t)
            target = cls._extract_target_word(t)
            axis = "width" if "ancho" in t else ("depth" if ("grosor" in t or "profundo" in t) else "height")
            return NormalizedIntent(
                intent_type=IntentType.MODIFY_ASSET,
                confidence=0.95,
                asset_id=active_asset_id,
                target_component=target,
                modifier_type=ModifierType.SET,
                property_name="dimensions",
                dimension_axis=axis,
                value=val if val is not None else 1.0,
                raw_text=raw_text
            )

        # Fallback de modificación general
        val = cls.parse_dimension_value(t)
        target = cls._extract_target_word(t)
        if val is not None:
            return NormalizedIntent(
                intent_type=IntentType.MODIFY_ASSET,
                confidence=0.85,
                asset_id=active_asset_id,
                target_component=target,
                modifier_type=ModifierType.SET,
                property_name="dimensions",
                dimension_axis="height",
                value=val,
                raw_text=raw_text
            )

        return NormalizedIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.20,
            asset_id=active_asset_id,
            raw_text=raw_text,
            clarification_needed=True,
            clarification_question="No pude determinar la intención exacta de la petición."
        )

    @classmethod
    def _extract_target_word(cls, text: str) -> Optional[str]:
        words = ["hoja", "blade", "mango", "handle", "guarda", "guard", "pomo", "pommel", "asiento", "seat", "pata", "leg", "cuerpo", "body", "base", "cubo", "cube", "barril", "barrel"]
        for w in words:
            if w in text:
                return w
        return None
