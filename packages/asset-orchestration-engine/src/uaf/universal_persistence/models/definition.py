"""
Universal Save, Load, Checkpoint, Profile, Settings, Configuration, Versioning, Migration & Data Persistence Models (UAF-81.62).
Normative domain models, enums, data contracts, and persistence structures.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class PersistenceScope(str, Enum):
    """Persistence scopes (§5)."""
    GLOBAL = "GLOBAL"
    USER = "USER"
    PROFILE = "PROFILE"
    SESSION = "SESSION"
    SAVE_SLOT = "SAVE_SLOT"
    CHECKPOINT = "CHECKPOINT"
    WORLD = "WORLD"
    PLAYER = "PLAYER"
    ACCOUNT = "ACCOUNT"
    NETWORK = "NETWORK"


class SaveOperationState(str, Enum):
    """States of an ongoing save/load lifecycle (§9)."""
    IDLE = "IDLE"
    QUEUED = "QUEUED"
    SNAPSHOTTING = "SNAPSHOTTING"
    SERIALIZING = "SERIALIZING"
    VALIDATING = "VALIDATING"
    WRITING = "WRITING"
    COMMITTING = "COMMITTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RECOVERING = "RECOVERING"


class SlotState(str, Enum):
    """Integrity and operational states of a save slot (§11)."""
    EMPTY = "EMPTY"
    VALID = "VALID"
    INVALID = "INVALID"
    CORRUPTED = "CORRUPTED"
    INCOMPATIBLE = "INCOMPATIBLE"
    MIGRATION_REQUIRED = "MIGRATION_REQUIRED"
    LOCKED = "LOCKED"
    BUSY = "BUSY"


class CheckpointType(str, Enum):
    """Runtime checkpoint categories (§23)."""
    WORLD = "WORLD"
    MISSION = "MISSION"
    QUEST = "QUEST"
    COMBAT = "COMBAT"
    AREA = "AREA"
    SCRIPT = "SCRIPT"
    MANUAL = "MANUAL"


class CheckpointLifetime(str, Enum):
    """Persistence retention policies for checkpoints (§24)."""
    SESSION_ONLY = "SESSION_ONLY"
    UNTIL_NEXT_CHECKPOINT = "UNTIL_NEXT_CHECKPOINT"
    UNTIL_SAVE = "UNTIL_SAVE"
    PERSISTENT = "PERSISTENT"


class SettingCategory(str, Enum):
    """Configuration categories (§33)."""
    GAMEPLAY = "GAMEPLAY"
    GRAPHICS = "GRAPHICS"
    AUDIO = "AUDIO"
    CONTROLS = "CONTROLS"
    ACCESSIBILITY = "ACCESSIBILITY"
    LANGUAGE = "LANGUAGE"
    DISPLAY = "DISPLAY"
    NETWORK = "NETWORK"
    UI = "UI"
    PRIVACY = "PRIVACY"


class SettingType(str, Enum):
    """Supported data types for persistent settings (§34)."""
    BOOL = "BOOL"
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    ENUM = "ENUM"
    COLOR = "COLOR"
    KEY_BINDING = "KEY_BINDING"
    VECTOR = "VECTOR"
    STRUCT = "STRUCT"


class SettingState(str, Enum):
    """Transactional states for individual settings (§36)."""
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    CONFIRMED = "CONFIRMED"
    REVERTED = "REVERTED"


class JournalState(str, Enum):
    """Crash recovery transaction journal states (§73)."""
    PREPARED = "PREPARED"
    WRITING = "WRITING"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    ABANDONED = "ABANDONED"


class CrashRecoveryPolicy(str, Enum):
    """Recovery policies following an ungraceful shutdown (§75)."""
    COMPLETE_COMMIT = "COMPLETE_COMMIT"
    ROLLBACK = "ROLLBACK"
    USE_LAST_VALID = "USE_LAST_VALID"
    QUARANTINE_CORRUPT = "QUARANTINE_CORRUPT"


class CloudConflictResolution(str, Enum):
    """Conflict resolution rules between local and remote saves (§210)."""
    LOCAL_WINS = "LOCAL_WINS"
    REMOTE_WINS = "REMOTE_WINS"
    NEWEST_WINS = "NEWEST_WINS"
    MANUAL_RESOLUTION = "MANUAL_RESOLUTION"
    MERGE = "MERGE"


class MultiplayerAuthority(str, Enum):
    """Authority models in multiplayer persistence (§211)."""
    SERVER_AUTHORITATIVE = "SERVER_AUTHORITATIVE"
    CLIENT_CACHE = "CLIENT_CACHE"
    SHARED_PROFILE = "SHARED_PROFILE"


class AutosaveTrigger(str, Enum):
    """Triggers capable of dispatching an autosave operation (§16)."""
    TIME = "TIME"
    LEVEL_CHANGE = "LEVEL_CHANGE"
    AREA_CHANGE = "AREA_CHANGE"
    QUEST_MILESTONE = "QUEST_MILESTONE"
    CHECKPOINT = "CHECKPOINT"
    MISSION_COMPLETE = "MISSION_COMPLETE"
    PLAYER_DEATH = "PLAYER_DEATH"
    MANUAL_EVENT = "MANUAL_EVENT"
    SYSTEM_EVENT = "SYSTEM_EVENT"


# ==============================================================================
# DATA STRUCTURES & VALUE OBJECTS
# ==============================================================================

@dataclass
class SaveRequest:
    """A formal request to persist data (§8)."""
    request_id: str
    slot_id: str
    scope: PersistenceScope = PersistenceScope.SAVE_SLOT
    priority: int = 10
    timestamp: float = 0.0
    schema_version: str = "1.0.0"
    requested_by: str = "system"


@dataclass
class SaveSlot:
    """Metadata and contents of a persistent save file (§10)."""
    slot_id: str
    profile_id: str = "default_profile"
    save_id: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    playtime: float = 0.0
    location: str = "World"
    version: str = "1.0.0"
    schema_version: str = "1.0.0"
    status: SlotState = SlotState.EMPTY
    thumbnail: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    payload: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def calculate_checksum(self) -> str:
        """Calculates deterministic SHA-256 integrity digest (§44)."""
        content_str = json.dumps({
            "slot_id": self.slot_id,
            "profile_id": self.profile_id,
            "save_id": self.save_id,
            "playtime": self.playtime,
            "version": self.version,
            "schema_version": self.schema_version,
            "payload": self.payload,
        }, sort_keys=True)
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()


@dataclass
class SaveManifest:
    """Header and discovery metadata for a save (§13)."""
    save_id: str
    slot_id: str
    profile_id: str
    timestamp: float
    playtime: float
    schema_version: str
    checksum: str
    modules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersistenceCheckpoint:
    """Recoverable runtime milestone (§22, §23)."""
    checkpoint_id: str
    checkpoint_type: CheckpointType = CheckpointType.MANUAL
    lifetime: CheckpointLifetime = CheckpointLifetime.PERSISTENT
    created_at: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True


@dataclass
class PlayerProfile:
    """Character progress, achievements, and stats (§26, §27)."""
    profile_id: str
    player_name: str = "Player"
    level: int = 1
    experience: int = 0
    progression: Dict[str, Any] = field(default_factory=dict)
    unlocks: Set[str] = field(default_factory=set)
    statistics: Dict[str, Any] = field(default_factory=dict)
    achievements: Set[str] = field(default_factory=set)
    inventory: Dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0


@dataclass
class UserProfile:
    """Account-level configurations and hardware preferences (§28)."""
    user_id: str
    username: str = "User"
    language: str = "en"
    input_bindings: Dict[str, str] = field(default_factory=dict)
    accessibility_options: Dict[str, Any] = field(default_factory=dict)
    audio_preferences: Dict[str, Any] = field(default_factory=dict)
    graphics_preferences: Dict[str, Any] = field(default_factory=dict)
    ui_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SettingEntry:
    """Individual typed configuration variable (§35)."""
    key: str
    category: SettingCategory
    setting_type: SettingType
    value: Any
    default_value: Any
    state: SettingState = SettingState.CONFIRMED
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    is_readonly: bool = False

    def validate(self, new_value: Any) -> bool:
        """Validates new value against bounds and allowed values."""
        if self.is_readonly:
            return False
        if self.allowed_values is not None and new_value not in self.allowed_values:
            return False
        if isinstance(new_value, (int, float)):
            if self.min_value is not None and new_value < self.min_value:
                return False
            if self.max_value is not None and new_value > self.max_value:
                return False
        return True


@dataclass
class SettingsStore:
    """Collection of managed settings with transactional safety (§32)."""
    settings: Dict[str, SettingEntry] = field(default_factory=dict)

    def register(self, entry: SettingEntry) -> None:
        self.settings[entry.key] = entry

    def get_value(self, key: str, fallback: Any = None) -> Any:
        if key in self.settings:
            return self.settings[key].value
        return fallback

    def set_value(self, key: str, value: Any) -> bool:
        if key not in self.settings:
            return False
        entry = self.settings[key]
        if not entry.validate(value):
            return False
        entry.value = value
        entry.state = SettingState.APPLIED
        return True


@dataclass
class SaveJournal:
    """Transaction log for atomic writes and crash recovery (§72, §73)."""
    journal_id: str
    slot_id: str
    state: JournalState = JournalState.PREPARED
    timestamp: float = 0.0
    temp_data: Dict[str, Any] = field(default_factory=dict)
    backup_data: Optional[Dict[str, Any]] = None


@dataclass
class MigrationStep:
    """Single-version transformation step (§59)."""
    from_version: str
    to_version: str
    migration_id: str
    description: str = ""
    transform_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None


@dataclass
class MigrationChain:
    """Sequential sequence of migrations from source to target version (§60)."""
    steps: List[MigrationStep] = field(default_factory=list)

    def apply(self, data: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """Applies migration chain in linear succession."""
        current_data = dict(data)
        for step in self.steps:
            if step.transform_fn:
                current_data = step.transform_fn(current_data)
            current_data["schema_version"] = step.to_version
            if step.to_version == target_version:
                break
        return current_data


@dataclass
class SaveBackup:
    """Rotational or safety backup snapshot (§78, §79)."""
    backup_id: str
    slot_id: str
    timestamp: float
    payload: Dict[str, Any]
    checksum: str


@dataclass
class PersistenceDiagnosticReport:
    """Health and metrics report of the storage subsystem."""
    is_healthy: bool = True
    total_slots: int = 0
    valid_slots: int = 0
    corrupt_slots: int = 0
    pending_transactions: int = 0
    active_checkpoints: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
