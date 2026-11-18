from typing import Dict, Any, List, Optional
from ..core.knowledge_types import KnowledgeStatus
from ..core.knowledge_schema import ObservationRecord

class KnowledgeLearningPipeline:
    def __init__(self):
        self.observations: Dict[str, ObservationRecord] = {}

    def record_repair_observation(self, rule_signature: str, succeeded: bool, evidence: str = "") -> ObservationRecord:
        if rule_signature not in self.observations:
            obs_id = f"OBS_{len(self.observations) + 1:04d}"
            self.observations[rule_signature] = ObservationRecord(
                observation_id=obs_id,
                rule_signature=rule_signature,
                success_count=1 if succeeded else 0,
                fail_count=0 if succeeded else 1,
                confidence=0.90 if succeeded else 0.50,
                status=KnowledgeStatus.PROPOSED,
                evidence=evidence
            )
        else:
            rec = self.observations[rule_signature]
            if succeeded:
                rec.success_count += 1
            else:
                rec.fail_count += 1
            total = rec.success_count + rec.fail_count
            rec.confidence = round(rec.success_count / total, 3)

        return self.observations[rule_signature]

    def promote_to_approved(self, rule_signature: str, has_formal_tests: bool = False) -> str:
        if rule_signature not in self.observations:
            raise KeyError(f"No observation record found for '{rule_signature}'.")
        rec = self.observations[rule_signature]
        if rec.confidence < 0.90 or rec.success_count < 2:
            raise ValueError(f"INSUFFICIENT_EVIDENCE: Cannot promote rule with confidence {rec.confidence} (< 0.90) and {rec.success_count} successes.")
        if not has_formal_tests:
            raise ValueError("VERIFICATION_REQUIRED: Rule promotion requires formal test evidence.")
        
        rec.status = KnowledgeStatus.APPROVED
        return f"Rule '{rule_signature}' successfully promoted to APPROVED production knowledge."
