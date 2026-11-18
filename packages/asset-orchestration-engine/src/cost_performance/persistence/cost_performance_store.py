import os
import json
import threading
from typing import Dict, Any, List, Optional
from .audit_trail import AuditRecord

class CostPerformanceStore:
    """Thread-safe transactional JSON store for optimization plans and audit records."""

    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\CostPerformance\darx_cost_performance_store.json"
        self._plans: Dict[str, Dict[str, Any]] = {}
        self._audit_records: List[AuditRecord] = []
        self._lock = threading.RLock()
        self.load_from_disk()

    def store_plan(self, plan_id: str, plan_dict: Dict[str, Any]):
        with self._lock:
            self._plans[plan_id] = plan_dict
            self.save_to_disk()

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._plans.get(plan_id)

    def list_plans(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._plans.values())

    def record_audit(self, audit: AuditRecord):
        with self._lock:
            self._audit_records.append(audit)
            self.save_to_disk()

    def list_audits(self) -> List[AuditRecord]:
        with self._lock:
            return list(self._audit_records)

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            data = {
                "plans": self._plans,
                "audits": [a.to_dict() for a in self._audit_records]
            }
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
                    self._plans = data.get("plans", {})
                    for a in data.get("audits", []):
                        self._audit_records.append(AuditRecord(**a))
            except Exception as e:
                print(f"[CostPerformanceStore] Warning loading store: {e}")
