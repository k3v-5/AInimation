from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

class IntentType(str, Enum):
    CREATE_ASSET = "CREATE_ASSET"
    MODIFY_ASSET = "MODIFY_ASSET"
    DELETE_ASSET = "DELETE_ASSET"
    DUPLICATE_ASSET = "DUPLICATE_ASSET"
    INSPECT_ASSET = "INSPECT_ASSET"
    VALIDATE_ASSET = "VALIDATE_ASSET"
    UNDO_CHANGE = "UNDO_CHANGE"
    REDO_CHANGE = "REDO_CHANGE"
    UNKNOWN = "UNKNOWN"

class ModifierType(str, Enum):
    SET = "SET"                # Valor absoluto (ej: "hazlo de 2m" -> 2.0)
    INCREMENT = "INCREMENT"    # Suma/resta relativa (ej: "agrega 20cm" -> +0.20)
    MULTIPLY = "MULTIPLY"      # Factor porcentual (ej: "20% más grande" -> *1.20)

@dataclass
class NormalizedIntent:
    intent_type: IntentType
    confidence: float = 1.0
    asset_id: Optional[str] = None
    target_component: Optional[str] = None
    modifier_type: ModifierType = ModifierType.SET
    property_name: str = "dimensions"
    dimension_axis: Optional[str] = None # 'height', 'width', 'depth', 'total_length', 'all'
    value: Any = None
    raw_text: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    clarification_needed: bool = False
    clarification_question: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
