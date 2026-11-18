import hashlib
import json
from typing import Dict, Any

class JobHasher:
    @classmethod
    def compute_checkpoint_hash(
        cls,
        job_id: str,
        phase: str,
        step: str,
        state_hash: str,
        prev_hash: str
    ) -> str:
        data = {
            "job_id": job_id,
            "phase": phase,
            "step": step,
            "state_hash": state_hash,
            "prev_hash": prev_hash or "ROOT"
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
