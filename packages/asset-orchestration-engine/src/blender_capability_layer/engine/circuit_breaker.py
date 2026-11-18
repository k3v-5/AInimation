from typing import Dict, Any
from ..core.capability_types import CircuitState

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.state = CircuitState.CLOSED
        self.failure_count = 0

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def allow_execution(self) -> bool:
        return self.state != CircuitState.OPEN

    def reset(self):
        self.state = CircuitState.HALF_OPEN
        self.failure_count = 0
