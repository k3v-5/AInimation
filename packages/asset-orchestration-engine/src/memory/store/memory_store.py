import os
import json
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from ..core.memory_types import MemoryRecord, MemoryScope, MemoryType, MemoryStatus, MemorySource
from ..core.exceptions import MemoryNotFoundError

class MemoryStore:
    """
    Persistent Memory Store for AOE (F73).
    Supports multi-scope storage, immutable versioning, asset semantic linking,
    disk persistence, and querying.
    """
    def __init__(self, persistence_path: Optional[str] = None):
        self._records: Dict[str, MemoryRecord] = {}
        self._lock = threading.RLock()
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\MemoryStore\darx_memory_store.json"
        
        # Load from disk if file exists
        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load_from_disk()

    def create(self, record: MemoryRecord) -> MemoryRecord:
        with self._lock:
            record.updated_at = time.time()
            record.memory_hash = record.compute_hash()
            self._records[record.memory_id] = record
            self.save_to_disk()
            return record

    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        with self._lock:
            return self._records.get(memory_id)

    def update(self, record: MemoryRecord) -> MemoryRecord:
        with self._lock:
            if record.memory_id not in self._records:
                raise MemoryNotFoundError(f"Memory {record.memory_id} not found.")
            record.updated_at = time.time()
            record.memory_hash = record.compute_hash()
            self._records[record.memory_id] = record
            self.save_to_disk()
            return record

    def supersede(self, old_memory_id: str, new_record: MemoryRecord) -> MemoryRecord:
        with self._lock:
            old = self._records.get(old_memory_id)
            if old:
                old.status = MemoryStatus.SUPERSEDED
                old.superseded_by = new_record.memory_id
                old.updated_at = time.time()
                old.memory_hash = old.compute_hash()
            new_record.version = (old.version + 1) if old else 1
            return self.create(new_record)

    def invalidate(self, memory_id: str, reason: str = ""):
        with self._lock:
            rec = self._records.get(memory_id)
            if rec:
                rec.status = MemoryStatus.INVALIDATED
                rec.metadata["invalidation_reason"] = reason
                rec.updated_at = time.time()
                rec.memory_hash = rec.compute_hash()
                self.save_to_disk()

    def archive(self, memory_id: str):
        with self._lock:
            rec = self._records.get(memory_id)
            if rec:
                rec.status = MemoryStatus.ARCHIVED
                rec.updated_at = time.time()
                self.save_to_disk()

    def list_all(self, status: Optional[MemoryStatus] = MemoryStatus.ACTIVE) -> List[MemoryRecord]:
        with self._lock:
            if status is None:
                return list(self._records.values())
            return [r for r in self._records.values() if r.status == status]

    def list_by_scope(self, scope: MemoryScope, status: Optional[MemoryStatus] = MemoryStatus.ACTIVE) -> List[MemoryRecord]:
        with self._lock:
            return [r for r in self.list_all(status) if r.scope == scope]

    def list_by_asset(self, semantic_id: str, status: Optional[MemoryStatus] = MemoryStatus.ACTIVE) -> List[MemoryRecord]:
        with self._lock:
            return [r for r in self.list_all(status) if r.semantic_id == semantic_id or r.scope == MemoryScope.PROJECT or r.scope == MemoryScope.GLOBAL]

    def list_by_task(self, task_id: str) -> List[MemoryRecord]:
        with self._lock:
            return [r for r in self.list_all(status=None) if r.task_id == task_id]

    def query(
        self,
        scope: Optional[MemoryScope] = None,
        memory_type: Optional[MemoryType] = None,
        semantic_id: Optional[str] = None,
        job_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[MemoryStatus] = MemoryStatus.ACTIVE,
        min_confidence: float = 0.0,
        tag: Optional[str] = None
    ) -> List[MemoryRecord]:
        with self._lock:
            results = self.list_all(status)
            if scope:
                results = [r for r in results if r.scope == scope]
            if memory_type:
                results = [r for r in results if r.memory_type == memory_type]
            if semantic_id:
                results = [r for r in results if r.semantic_id == semantic_id or r.scope in (MemoryScope.PROJECT, MemoryScope.GLOBAL)]
            if job_id:
                results = [r for r in results if r.job_id == job_id]
            if agent_id:
                results = [r for r in results if r.agent_id == agent_id]
            if min_confidence > 0.0:
                results = [r for r in results if r.confidence >= min_confidence]
            if tag:
                results = [r for r in results if tag in r.tags]
            return results

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            data = {k: v.to_dict() for k, v in self._records.items()}
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
                    self._records = {k: MemoryRecord.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"[MemoryStore] Warning loading from disk: {e}")
