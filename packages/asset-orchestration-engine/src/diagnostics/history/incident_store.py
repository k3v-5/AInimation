import os
import json
import threading
from typing import Dict, Any, List, Optional
from ..core.failure_models import FailureRecord

class IncidentStore:
    """Thread-safe persistent storage for failure records and diagnostic incident history."""
    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\Diagnostics\darx_incident_store.json"
        self._lock = threading.RLock()
        self._incidents: Dict[str, FailureRecord] = {}

        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load_from_disk()

    def store_incident(self, failure: FailureRecord):
        with self._lock:
            self._incidents[failure.failure_id] = failure
            self.save_to_disk()

    def get_incident(self, failure_id: str) -> Optional[FailureRecord]:
        with self._lock:
            return self._incidents.get(failure_id)

    def list_incidents(self, semantic_id: Optional[str] = None) -> List[FailureRecord]:
        with self._lock:
            all_inc = list(self._incidents.values())
            if semantic_id:
                return [i for i in all_inc if i.semantic_id == semantic_id]
            return all_inc

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            payload = {k: v.to_dict() for k, v in self._incidents.items()}
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

    def load_from_disk(self):
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        if os.path.getsize(self.persistence_path) == 0:
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._incidents = {k: FailureRecord.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"[IncidentStore] Warning loading store: {e}")
