import os
import json
import threading
from typing import Dict, Any, List, Optional
from ..core.failure_models import FailureRecord

class FailureStore:
    """Thread-safe transactional JSON store for persistent FailureRecord instances."""

    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\FailureAnalysis\darx_failure_store.json"
        self._failures: Dict[str, FailureRecord] = {}
        self._lock = threading.RLock()
        self.load_from_disk()

    def store_failure(self, failure: FailureRecord):
        with self._lock:
            self._failures[failure.failure_id] = failure
            self.save_to_disk()

    def get_failure(self, failure_id: str) -> Optional[FailureRecord]:
        with self._lock:
            return self._failures.get(failure_id)

    def list_failures(self) -> List[FailureRecord]:
        with self._lock:
            return list(self._failures.values())

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            data = {k: v.to_dict() for k, v in self._failures.items()}
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_disk(self):
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        if os.path.getsize(self.persistence_path) == 0:
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._failures = {k: FailureRecord.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"[FailureStore] Warning loading failures: {e}")
