"""
Universal Save, Load, Checkpoint, Profile, Settings, Configuration, Versioning, Migration & Data Persistence System (UAF-81.62).
Authoritative persistence framework for the Asset Orchestration Engine.
"""

from .models import (
    PersistenceScope,
    SaveOperationState,
    SlotState,
    CheckpointType,
    CheckpointLifetime,
    SettingCategory,
    SettingType,
    SettingState,
    JournalState,
    CrashRecoveryPolicy,
    CloudConflictResolution,
    MultiplayerAuthority,
    AutosaveTrigger,
    SaveRequest,
    SaveSlot,
    SaveManifest,
    PersistenceCheckpoint,
    PlayerProfile,
    UserProfile,
    SettingEntry,
    SettingsStore,
    SaveJournal,
    MigrationStep,
    MigrationChain,
    SaveBackup,
    PersistenceDiagnosticReport,
)

from .engine import UniversalPersistenceFabricator
from .validation import UniversalPersistenceValidator, PersistenceValidationReport
from .package import UniversalPersistencePackager, ProductionReadyPersistence

__all__ = [
    "PersistenceScope",
    "SaveOperationState",
    "SlotState",
    "CheckpointType",
    "CheckpointLifetime",
    "SettingCategory",
    "SettingType",
    "SettingState",
    "JournalState",
    "CrashRecoveryPolicy",
    "CloudConflictResolution",
    "MultiplayerAuthority",
    "AutosaveTrigger",
    "SaveRequest",
    "SaveSlot",
    "SaveManifest",
    "PersistenceCheckpoint",
    "PlayerProfile",
    "UserProfile",
    "SettingEntry",
    "SettingsStore",
    "SaveJournal",
    "MigrationStep",
    "MigrationChain",
    "SaveBackup",
    "PersistenceDiagnosticReport",
    "UniversalPersistenceFabricator",
    "UniversalPersistenceValidator",
    "PersistenceValidationReport",
    "UniversalPersistencePackager",
    "ProductionReadyPersistence",
]
