import hashlib
import json
from typing import List, Set, Tuple
from ..core.governance_schema import ActionProposal

class DuplicateActionDetector:
    def __init__(self):
        self.seen_fingerprints: Set[str] = set()

    def check_duplicate(self, proposal: ActionProposal) -> Tuple[bool, str]:
        fp = self.compute_fingerprint(proposal)
        if fp in self.seen_fingerprints:
            return True, f"DUPLICATE_ACTION: Proposal '{proposal.action_name}' on '{proposal.target_entity}' with identical parameters was already executed."
        self.seen_fingerprints.add(fp)
        return False, "Not duplicate."

    def clear(self):
        self.seen_fingerprints.clear()

    @staticmethod
    def compute_fingerprint(proposal: ActionProposal) -> str:
        payload = {
            "action": proposal.action_name,
            "target": proposal.target_entity,
            "params": proposal.parameters
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

class ExecutionLoopGuard:
    def __init__(self, max_cycle_len: int = 4):
        self.history: List[str] = []

    def record_and_check_loop(self, fingerprint: str) -> Tuple[bool, str]:
        self.history.append(fingerprint)
        if len(self.history) >= 4:
            # Ciclo A -> B -> A -> B
            if self.history[-1] == self.history[-3] and self.history[-2] == self.history[-4]:
                return True, "LOOP_DETECTED: Alternating action pattern detected across iterations."
        if len(self.history) >= 3:
            # Ciclo A -> A -> A
            if self.history[-1] == self.history[-2] == self.history[-3]:
                return True, "LOOP_DETECTED: Repeated identical action pattern detected."
        return False, "Normal."
