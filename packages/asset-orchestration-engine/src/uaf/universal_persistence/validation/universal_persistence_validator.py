"""
Universal Persistence Validator (UAF-81.62).
Validates integrity, cryptographic checksums, schemas, size bounds, and security contracts.
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

from ..models import SaveSlot, SlotState, SettingEntry, PersistenceCheckpoint


@dataclass
class PersistenceValidationReport:
    """Detailed validation evaluation report."""
    is_valid: bool = True
    status: SlotState = SlotState.VALID
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class UniversalPersistenceValidator:
    """
    Integrity and security validator for persistence slots, profiles, and settings.
    """

    FORBIDDEN_ID_CHARS = set(r'\/:*?"<>|..')
    SENSITIVE_KEYS = {"password", "secret", "api_key", "token", "private_key"}

    def __init__(
        self,
        max_payload_bytes: int = 10 * 1024 * 1024,
        max_collection_items: int = 10000,
        max_recursion_depth: int = 20,
    ):
        self.max_payload_bytes = max_payload_bytes
        self.max_collection_items = max_collection_items
        self.max_recursion_depth = max_recursion_depth

    def validate_slot_id(self, slot_id: str) -> Tuple[bool, str]:
        """Ensures slot ID does not perform path traversal or use illegal characters (§212)."""
        if not slot_id or not isinstance(slot_id, str):
            return False, "Slot ID cannot be empty or non-string."
        if ".." in slot_id or "/" in slot_id or "\\" in slot_id:
            return False, "Path traversal detected in slot ID."
        if any(c in self.FORBIDDEN_ID_CHARS for c in slot_id):
            return False, "Slot ID contains forbidden filesystem characters."
        if not re.match(r"^[a-zA-Z0-9_\-]+$", slot_id):
            return False, "Slot ID must contain only alphanumeric characters, underscores, or dashes."
        return True, "Valid slot ID."

    def validate_profile_id(self, profile_id: str) -> Tuple[bool, str]:
        """Ensures profile ID does not perform path traversal (§212)."""
        if not profile_id or not isinstance(profile_id, str):
            return False, "Profile ID cannot be empty or non-string."
        if ".." in profile_id or "/" in profile_id or "\\" in profile_id:
            return False, "Path traversal detected in profile ID."
        if not re.match(r"^[a-zA-Z0-9_\-]+$", profile_id):
            return False, "Profile ID must contain only alphanumeric characters, underscores, or dashes."
        return True, "Valid profile ID."

    def validate_checksum(self, slot: SaveSlot) -> bool:
        """Verifies SHA-256 integrity hash against slot content (§44, §83)."""
        expected = slot.calculate_checksum()
        return slot.checksum == expected

    def check_recursion_depth(self, obj: Any, current_depth: int = 0) -> bool:
        """Protects against deeply nested or recursive deserialization attacks (§212)."""
        if current_depth > self.max_recursion_depth:
            return False
        if isinstance(obj, dict):
            return all(self.check_recursion_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, (list, tuple, set)):
            return all(self.check_recursion_depth(item, current_depth + 1) for item in obj)
        return True

    def scan_for_secrets(self, data: Any) -> List[str]:
        """Checks if unencrypted secrets or tokens are present in persistence data (§212)."""
        found = []
        if isinstance(data, dict):
            for k, v in data.items():
                if any(sec in k.lower() for sec in self.SENSITIVE_KEYS):
                    found.append(f"Secret detected in key: '{k}'")
                found.extend(self.scan_for_secrets(v))
        elif isinstance(data, (list, tuple)):
            for item in data:
                found.extend(self.scan_for_secrets(item))
        return found

    def validate_save_slot(
        self,
        slot: SaveSlot,
        known_schemas: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> PersistenceValidationReport:
        """Comprehensive verification of a save slot (§83, §204, §205)."""
        report = PersistenceValidationReport()

        # 1. Slot ID & Profile ID security checks
        valid_sid, sid_msg = self.validate_slot_id(slot.slot_id)
        if not valid_sid:
            report.is_valid = False
            report.status = SlotState.INVALID
            report.errors.append(f"Slot ID security failure: {sid_msg}")

        valid_pid, pid_msg = self.validate_profile_id(slot.profile_id)
        if not valid_pid:
            report.is_valid = False
            report.status = SlotState.INVALID
            report.errors.append(f"Profile ID security failure: {pid_msg}")

        # 2. Checksum integrity
        if not self.validate_checksum(slot):
            report.is_valid = False
            report.status = SlotState.CORRUPTED
            report.errors.append("SHA-256 checksum mismatch: data has been modified or corrupted.")

        # 3. Payload size check
        try:
            raw_bytes = json.dumps(slot.payload).encode("utf-8")
            report.metrics["payload_bytes"] = len(raw_bytes)
            if len(raw_bytes) > self.max_payload_bytes:
                report.is_valid = False
                report.status = SlotState.INVALID
                report.errors.append(f"Payload size ({len(raw_bytes)} bytes) exceeds maximum limit ({self.max_payload_bytes}).")
        except (TypeError, ValueError) as ex:
            report.is_valid = False
            report.status = SlotState.CORRUPTED
            report.errors.append(f"Serialization failed: {ex}")

        # 4. Recursion attack detection
        if not self.check_recursion_depth(slot.payload):
            report.is_valid = False
            report.status = SlotState.INVALID
            report.errors.append("Recursion limit exceeded in payload structure.")

        # 5. Secret redaction check
        secrets = self.scan_for_secrets(slot.payload)
        secrets.extend(self.scan_for_secrets(slot.metadata))
        if secrets:
            report.warnings.extend(secrets)

        # 6. Schema check
        if known_schemas and slot.schema_version in known_schemas:
            schema = known_schemas[slot.schema_version]
            req_fields = schema.get("fields", [])
            for rf in req_fields:
                if rf not in slot.payload:
                    report.warnings.append(f"Schema {slot.schema_version} field '{rf}' is missing from payload.")
        elif known_schemas and slot.schema_version not in known_schemas:
            report.status = SlotState.INCOMPATIBLE
            report.warnings.append(f"Schema version '{slot.schema_version}' is not recognized.")

        return report
