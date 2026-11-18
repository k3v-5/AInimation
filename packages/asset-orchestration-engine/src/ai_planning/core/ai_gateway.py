from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
import time

class RequestSource(str, Enum):
    USER = "USER"
    AI = "AI"
    SYSTEM = "SYSTEM"
    AUTOMATION = "AUTOMATION"
    TEST = "TEST"

@dataclass
class AIRequest:
    request_id: str
    user_text: str
    source: RequestSource = RequestSource.USER
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class AIRequestGateway:
    def __init__(self):
        self.request_cache: Dict[str, Dict[str, Any]] = {} # request_id -> result

    def receive_request(self, request: AIRequest) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Garantiza Idempotencia.
        Si la petición ya fue procesada, devuelve (True, resultado_previo).
        Si es nueva, devuelve (False, None).
        """
        if request.request_id in self.request_cache:
            return True, self.request_cache[request.request_id]
        return False, None

    def store_result(self, request_id: str, result: Dict[str, Any]):
        self.request_cache[request_id] = result
