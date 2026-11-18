import os
import json
import threading
from typing import Dict, Any, List, Optional
from ..core.production_job import ProductionJob

class ProductionStore:
    """Thread-safe transactional JSON store for ProductionJobs and Plans."""

    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\Production\darx_production_store.json"
        self._jobs: Dict[str, ProductionJob] = {}
        self._plans: Dict[str, Dict[str, Any]] = {}
        self._manifests: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.load_from_disk()

    def store_job(self, job: ProductionJob):
        with self._lock:
            self._jobs[job.job_id] = job
            self.save_to_disk()

    def get_job(self, job_id: str) -> Optional[ProductionJob]:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self) -> List[ProductionJob]:
        with self._lock:
            return list(self._jobs.values())

    def store_plan(self, plan_id: str, plan_dict: Dict[str, Any]):
        with self._lock:
            self._plans[plan_id] = plan_dict
            self.save_to_disk()

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._plans.get(plan_id)

    def store_manifest(self, job_id: str, manifest: Dict[str, Any]):
        with self._lock:
            self._manifests[job_id] = manifest
            self.save_to_disk()

    def get_manifest(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._manifests.get(job_id)

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            data = {
                "jobs": {k: v.to_dict() for k, v in self._jobs.items()},
                "plans": self._plans,
                "manifests": self._manifests
            }
            tmp_path = self.persistence_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.persistence_path)

    def load_from_disk(self):
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        if os.path.getsize(self.persistence_path) == 0:
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.get("jobs", {}).items():
                        self._jobs[k] = ProductionJob.from_dict(v)
                    self._plans = data.get("plans", {})
                    self._manifests = data.get("manifests", {})
            except Exception as e:
                print(f"[ProductionStore] Warning loading store: {e}")
