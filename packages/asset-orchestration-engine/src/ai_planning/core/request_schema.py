from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
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
