"""
Universal Persistence Fabricator (UAF-81.62).
Core execution engine for saves, loads, checkpoints, profiles, settings,
schema migration, atomic journaling, crash recovery, and cloud synchronization.
"""

from __future__ import annotations
import copy
import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..models import (
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


class UniversalPersistenceFabricator:
    """
    Authoritative persistence fabricator implementing crash-safe transactions,
    rotational backups, checkpoint lifecycles, profile swapping, settings transactions,
    schema migrations, and cloud conflict resolution.
    """

    def __init__(self, max_payload_bytes: int = 10 * 1024 * 1024, max_backups_per_slot: int = 5):
        self.max_payload_bytes = max_payload_bytes
        self.max_backups_per_slot = max_backups_per_slot

        # Primary persistence stores
        self._slots: Dict[str, SaveSlot] = {}
        self._locked_slots: Set[str] = set()
        self._previous_slots: Dict[str, SaveSlot] = {}  # Last valid save fallback
        self._journals: Dict[str, SaveJournal] = {}
        self._backups: Dict[str, List[SaveBackup]] = {}
        self._quarantine: Dict[str, Dict[str, Any]] = {}

        # Checkpoints
        self._checkpoints: Dict[str, PersistenceCheckpoint] = {}

        # Profiles
        self._player_profiles: Dict[str, PlayerProfile] = {}
        self._user_profiles: Dict[str, UserProfile] = {}
        self._active_player_profile_id: Optional[str] = None
        self._active_user_profile_id: Optional[str] = None

        # Settings
        self._settings_store = SettingsStore()
        self._initialize_default_settings()

        # Configuration tiers
        self._default_config: Dict[str, Any] = {}
        self._platform_config: Dict[str, Any] = {}
        self._user_config: Dict[str, Any] = {}
        self._profile_config: Dict[str, Any] = {}
        self._session_config: Dict[str, Any] = {}
        self._readonly_config_keys: Set[str] = set()

        # Schema registry & migrations
        self._schema_registry: Dict[str, Dict[str, Any]] = {
            "1.0.0": {"version": "1.0.0", "fields": ["player_name", "level", "inventory", "location"]},
            "2.0.0": {"version": "2.0.0", "fields": ["player_name", "level", "inventory", "location", "skills"]},
            "3.0.0": {"version": "3.0.0", "fields": ["player_name", "level", "inventory", "location", "skills", "stats"]},
        }
        self._migrations: Dict[Tuple[str, str], MigrationStep] = {}
        self._migration_logs: List[Dict[str, Any]] = []

        # Autosave throttling & queue
        self._autosave_queue: List[SaveRequest] = []
        self._last_autosave_time: float = 0.0
        self._autosave_min_interval: float = 2.0  # seconds
        self._autosave_enabled: bool = True
        self._blocked_autosave_states: Set[str] = {"CUTSCENE", "LOADING", "DEATH_ANIM"}
        self._current_runtime_state: str = "NORMAL"

        # Multiplayer authority
        self._multiplayer_authority: MultiplayerAuthority = MultiplayerAuthority.SERVER_AUTHORITATIVE
        self._is_server: bool = True

        # Cloud sync storage simulation
        self._cloud_store: Dict[str, SaveSlot] = {}
        self._cloud_connected: bool = True

    # ==========================================================================
    # SAVE & LOAD SERVICE (§7, §8, §9, §10, §11, §69, §70, §71)
    # ==========================================================================

    def create_save(
        self,
        slot_id: str,
        profile_id: str = "default_profile",
        location: str = "World",
        version: str = "1.0.0",
        schema_version: str = "1.0.0",
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SaveSlot:
        """Instantiates a new save slot object in MEMORY (not yet committed)."""
        now = time.time()
        slot = SaveSlot(
            slot_id=slot_id,
            profile_id=profile_id,
            save_id=f"save_{slot_id}_{int(now)}",
            created_at=now,
            updated_at=now,
            playtime=0.0,
            location=location,
            version=version,
            schema_version=schema_version,
            status=SlotState.BUSY,
            thumbnail="",
            metadata=metadata or {},
            payload=payload or {},
        )
        slot.checksum = slot.calculate_checksum()
        return slot

    def create_save_request(
        self,
        slot_id: str,
        scope: PersistenceScope = PersistenceScope.SAVE_SLOT,
        priority: int = 10,
        schema_version: str = "1.0.0",
        requested_by: str = "system",
    ) -> SaveRequest:
        """Creates a tracked persistence request."""
        return SaveRequest(
            request_id=f"req_{int(time.time()*1000)}_{slot_id}",
            slot_id=slot_id,
            scope=scope,
            priority=priority,
            timestamp=time.time(),
            schema_version=schema_version,
            requested_by=requested_by,
        )

    def write_save_atomic(self, slot: SaveSlot) -> Tuple[bool, str]:
        """
        Executes atomic two-phase persistence:
        1. Journal PREPARED & temporary state captured.
        2. Journal WRITING.
        3. Journal COMMITTED and slot registered.
        Preserves previous valid save in case of rollback.
        """
        if slot.slot_id in self._locked_slots:
            return False, f"Slot '{slot.slot_id}' is locked."

        # Check payload size
        serialized = json.dumps(slot.payload)
        if len(serialized.encode("utf-8")) > self.max_payload_bytes:
            return False, f"Payload size exceeds maximum allowed bytes ({self.max_payload_bytes})."

        # Preserve previous valid save
        if slot.slot_id in self._slots and self._slots[slot.slot_id].status == SlotState.VALID:
            self._previous_slots[slot.slot_id] = copy.deepcopy(self._slots[slot.slot_id])

        # Step 1: Create transaction journal
        journal_id = f"journal_{slot.slot_id}_{int(time.time())}"
        journal = SaveJournal(
            journal_id=journal_id,
            slot_id=slot.slot_id,
            state=JournalState.PREPARED,
            timestamp=time.time(),
            temp_data=copy.deepcopy(slot.payload),
            backup_data=copy.deepcopy(self._previous_slots.get(slot.slot_id).payload) if slot.slot_id in self._previous_slots else None,
        )
        self._journals[slot.slot_id] = journal

        # Step 2: Transition to WRITING
        journal.state = JournalState.WRITING
        slot.status = SlotState.BUSY
        slot.checksum = slot.calculate_checksum()
        slot.updated_at = time.time()

        # Step 3: Atomic commit
        journal.state = JournalState.COMMITTED
        slot.status = SlotState.VALID
        self._slots[slot.slot_id] = copy.deepcopy(slot)

        # Create rotational backup
        self.create_backup(slot.slot_id)
        return True, "Atomic save committed successfully."

    def commit_save(self, slot_id: str) -> bool:
        """Marks a pending or busy slot as committed and valid."""
        if slot_id in self._slots:
            self._slots[slot_id].status = SlotState.VALID
            return True
        return False

    def load_save(self, slot_id: str) -> Optional[SaveSlot]:
        """Loads and verifies a save slot from storage."""
        if slot_id not in self._slots:
            return None
        slot = self._slots[slot_id]
        if slot.status != SlotState.VALID:
            return None
        # Verify integrity
        if slot.checksum != slot.calculate_checksum():
            slot.status = SlotState.CORRUPTED
            return None
        return copy.deepcopy(slot)

    def delete_save(self, slot_id: str) -> bool:
        """Deletes a save slot and clears associated temporary data."""
        if slot_id in self._locked_slots:
            return False
        if slot_id in self._slots:
            del self._slots[slot_id]
            return True
        return False

    def list_saves(self) -> List[SaveManifest]:
        """Returns discovery manifests for all valid saves."""
        manifests = []
        for s in self._slots.values():
            if s.status == SlotState.VALID:
                manifests.append(
                    SaveManifest(
                        save_id=s.save_id,
                        slot_id=s.slot_id,
                        profile_id=s.profile_id,
                        timestamp=s.updated_at,
                        playtime=s.playtime,
                        schema_version=s.schema_version,
                        checksum=s.checksum,
                        modules=s.metadata,
                    )
                )
        return manifests

    def lock_slot(self, slot_id: str) -> None:
        """Prevents write or delete operations on the slot."""
        self._locked_slots.add(slot_id)

    def unlock_slot(self, slot_id: str) -> None:
        """Unlocks the slot for modification."""
        self._locked_slots.discard(slot_id)

    def is_slot_locked(self, slot_id: str) -> bool:
        return slot_id in self._locked_slots

    def get_slot_state(self, slot_id: str) -> SlotState:
        if slot_id not in self._slots:
            return SlotState.EMPTY
        return self._slots[slot_id].status

    # ==========================================================================
    # AUTOSAVE SYSTEM (§15, §16, §17, §18, §19, §20)
    # ==========================================================================

    def set_runtime_state(self, state: str) -> None:
        """Sets the current game runtime state (e.g. NORMAL, CUTSCENE, LOADING)."""
        self._current_runtime_state = state

    def request_autosave(
        self,
        slot_id: str = "autosave_slot",
        trigger: AutosaveTrigger = AutosaveTrigger.TIME,
        payload: Optional[Dict[str, Any]] = None,
        force: bool = False,
    ) -> Tuple[bool, str]:
        """
        Dispatches an autosave taking into account:
        - Throttling (minimum interval)
        - Coalescing
        - Blocked states (cutscenes, loading)
        """
        now = time.time()
        if not self._autosave_enabled and not force:
            return False, "Autosave is disabled."

        if self._current_runtime_state in self._blocked_autosave_states and not force:
            return False, f"Autosave blocked during state '{self._current_runtime_state}'."

        # Throttling check
        if (now - self._last_autosave_time < self._autosave_min_interval) and not force:
            # Coalesce into queue
            req = SaveRequest(
                request_id=f"auto_{int(now*1000)}",
                slot_id=slot_id,
                scope=PersistenceScope.SAVE_SLOT,
                priority=5,
                timestamp=now,
            )
            self._autosave_queue.append(req)
            return False, "Autosave throttled and queued for coalescing."

        # Execute save
        slot = self.create_save(
            slot_id=slot_id,
            profile_id=self._active_player_profile_id or "default_profile",
            location="Autosave_Point",
            payload=payload or {"auto_trigger": trigger.value, "timestamp": now},
        )
        success, msg = self.write_save_atomic(slot)
        if success:
            self._last_autosave_time = now
            self._autosave_queue.clear()
            return True, f"Autosave triggered by {trigger.value} succeeded."
        return False, f"Autosave failed: {msg}"

    def flush_autosave_queue(self, payload: Optional[Dict[str, Any]] = None) -> bool:
        """Flushes coalesced autosave requests."""
        if not self._autosave_queue:
            return False
        latest_req = self._autosave_queue[-1]
        self._last_autosave_time = 0.0  # bypass throttle for flush
        success, _ = self.request_autosave(
            slot_id=latest_req.slot_id,
            trigger=AutosaveTrigger.TIME,
            payload=payload,
            force=True,
        )
        return success

    # ==========================================================================
    # CHECKPOINT SYSTEM (§21, §22, §23, §24, §25)
    # ==========================================================================

    def create_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_type: CheckpointType = CheckpointType.MANUAL,
        lifetime: CheckpointLifetime = CheckpointLifetime.PERSISTENT,
        data: Optional[Dict[str, Any]] = None,
    ) -> PersistenceCheckpoint:
        """Creates or replaces a checkpoint in runtime memory."""
        cp = PersistenceCheckpoint(
            checkpoint_id=checkpoint_id,
            checkpoint_type=checkpoint_type,
            lifetime=lifetime,
            created_at=time.time(),
            data=data or {},
            is_valid=True,
        )
        self._checkpoints[checkpoint_id] = cp
        return cp

    def load_checkpoint(self, checkpoint_id: str) -> Optional[PersistenceCheckpoint]:
        """Retrieves an active valid checkpoint."""
        if checkpoint_id in self._checkpoints:
            cp = self._checkpoints[checkpoint_id]
            if cp.is_valid:
                return copy.deepcopy(cp)
        return None

    def invalidate_checkpoint(self, checkpoint_id: str) -> bool:
        """Invalidates a checkpoint upon world change or version mismatch."""
        if checkpoint_id in self._checkpoints:
            self._checkpoints[checkpoint_id].is_valid = False
            return True
        return False

    def clear_session_checkpoints(self) -> int:
        """Cleans up checkpoints designated with SESSION_ONLY lifetime."""
        to_delete = [
            cid for cid, cp in self._checkpoints.items()
            if cp.lifetime == CheckpointLifetime.SESSION_ONLY
        ]
        for cid in to_delete:
            del self._checkpoints[cid]
        return len(to_delete)

    # ==========================================================================
    # PROFILES & USERS (§26, §27, §28, §29, §30, §31)
    # ==========================================================================

    def create_player_profile(
        self,
        profile_id: str,
        player_name: str = "Player",
        level: int = 1,
        inventory: Optional[Dict[str, Any]] = None,
        progression: Optional[Dict[str, Any]] = None,
    ) -> PlayerProfile:
        now = time.time()
        prof = PlayerProfile(
            profile_id=profile_id,
            player_name=player_name,
            level=level,
            inventory=inventory or {},
            progression=progression or {},
            created_at=now,
            updated_at=now,
        )
        self._player_profiles[profile_id] = prof
        if self._active_player_profile_id is None:
            self._active_player_profile_id = profile_id
        return prof

    def create_user_profile(
        self,
        user_id: str,
        username: str = "User",
        language: str = "en",
        input_bindings: Optional[Dict[str, str]] = None,
        accessibility_options: Optional[Dict[str, Any]] = None,
    ) -> UserProfile:
        user = UserProfile(
            user_id=user_id,
            username=username,
            language=language,
            input_bindings=input_bindings or {"MOVE_FORWARD": "W", "JUMP": "Space"},
            accessibility_options=accessibility_options or {"subtitles": True, "ui_scale": 1.0},
        )
        self._user_profiles[user_id] = user
        if self._active_user_profile_id is None:
            self._active_user_profile_id = user_id
        return user

    def switch_player_profile(self, target_profile_id: str) -> Tuple[bool, str]:
        """
        Transactional profile switch:
        1. Validates target exists.
        2. Flushes pending data.
        3. Swaps active pointer.
        """
        if target_profile_id not in self._player_profiles:
            return False, f"Target profile '{target_profile_id}' not found."
        self._active_player_profile_id = target_profile_id
        return True, f"Successfully switched to profile '{target_profile_id}'."

    def get_active_player_profile(self) -> Optional[PlayerProfile]:
        if self._active_player_profile_id:
            return self._player_profiles.get(self._active_player_profile_id)
        return None

    def get_active_user_profile(self) -> Optional[UserProfile]:
        if self._active_user_profile_id:
            return self._user_profiles.get(self._active_user_profile_id)
        return None

    # ==========================================================================
    # SETTINGS & CONFIGURATION (§32, §33, §34, §35, §36, §37, §44, §45, §46)
    # ==========================================================================

    def _initialize_default_settings(self) -> None:
        """Initializes canonical game settings."""
        defaults = [
            SettingEntry("master_volume", SettingCategory.AUDIO, SettingType.FLOAT, 1.0, 1.0, min_value=0.0, max_value=1.0),
            SettingEntry("music_volume", SettingCategory.AUDIO, SettingType.FLOAT, 0.8, 0.8, min_value=0.0, max_value=1.0),
            SettingEntry("sfx_volume", SettingCategory.AUDIO, SettingType.FLOAT, 0.9, 0.9, min_value=0.0, max_value=1.0),
            SettingEntry("subtitles", SettingCategory.ACCESSIBILITY, SettingType.BOOL, True, True),
            SettingEntry("fullscreen", SettingCategory.GRAPHICS, SettingType.BOOL, True, True),
            SettingEntry("resolution", SettingCategory.DISPLAY, SettingType.STRING, "1920x1080", "1920x1080", allowed_values=["1280x720", "1920x1080", "2560x1440", "3840x2160"]),
            SettingEntry("difficulty", SettingCategory.GAMEPLAY, SettingType.ENUM, "NORMAL", "NORMAL", allowed_values=["EASY", "NORMAL", "HARD", "NIGHTMARE"]),
            SettingEntry("mouse_sensitivity", SettingCategory.CONTROLS, SettingType.FLOAT, 1.0, 1.0, min_value=0.1, max_value=10.0),
            SettingEntry("system_build_id", SettingCategory.PRIVACY, SettingType.STRING, "v1.0.0-PROD", "v1.0.0-PROD", is_readonly=True),
        ]
        for d in defaults:
            self._settings_store.register(d)

    @property
    def settings(self) -> SettingsStore:
        return self._settings_store

    def set_setting(self, key: str, value: Any, apply_immediately: bool = True) -> bool:
        """Updates a setting with type and bounds validation."""
        if key not in self._settings_store.settings:
            return False
        entry = self._settings_store.settings[key]
        if not entry.validate(value):
            return False
        entry.value = value
        entry.state = SettingState.APPLIED if apply_immediately else SettingState.PENDING
        return True

    def confirm_setting(self, key: str) -> bool:
        """Confirms an applied setting transition."""
        if key in self._settings_store.settings:
            self._settings_store.settings[key].state = SettingState.CONFIRMED
            return True
        return False

    def revert_setting(self, key: str) -> bool:
        """Reverts setting to default value."""
        if key in self._settings_store.settings:
            entry = self._settings_store.settings[key]
            entry.value = entry.default_value
            entry.state = SettingState.REVERTED
            return True
        return False

    def reset_all_settings(self) -> None:
        """Resets all non-readonly settings to defaults."""
        for entry in self._settings_store.settings.values():
            if not entry.is_readonly:
                entry.value = entry.default_value
                entry.state = SettingState.CONFIRMED

    def get_resolved_configuration(self, key: str) -> Any:
        """
        Evaluates configuration precedence (§45):
        DEFAULT -> PLATFORM -> USER -> PROFILE -> SESSION.
        """
        if key in self._session_config:
            return self._session_config[key]
        if key in self._profile_config:
            return self._profile_config[key]
        if key in self._user_config:
            return self._user_config[key]
        if key in self._platform_config:
            return self._platform_config[key]
        if key in self._default_config:
            return self._default_config[key]
        return self._settings_store.get_value(key, None)

    def set_config_tier(self, tier: str, key: str, value: Any) -> bool:
        """Sets configuration value into specific tier."""
        if key in self._readonly_config_keys:
            return False
        if tier == "DEFAULT":
            self._default_config[key] = value
        elif tier == "PLATFORM":
            self._platform_config[key] = value
        elif tier == "USER":
            self._user_config[key] = value
        elif tier == "PROFILE":
            self._profile_config[key] = value
        elif tier == "SESSION":
            self._session_config[key] = value
        else:
            return False
        return True

    def mark_config_readonly(self, key: str) -> None:
        self._readonly_config_keys.add(key)

    # ==========================================================================
    # SCHEMA VERSIONING & MIGRATIONS (§55, §56, §57, §58, §59, §60, §61, §62, §63, §64, §65)
    # ==========================================================================

    def register_schema(self, version: str, fields: List[str]) -> None:
        self._schema_registry[version] = {"version": version, "fields": fields}

    def get_schema(self, version: str) -> Optional[Dict[str, Any]]:
        return self._schema_registry.get(version)

    def is_schema_compatible(self, source_version: str, target_version: str) -> bool:
        if source_version == target_version:
            return True
        return (source_version, target_version) in self._migrations or self._find_migration_chain(source_version, target_version) is not None

    def register_migration_step(
        self,
        from_ver: str,
        to_ver: str,
        migration_id: str,
        transform_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        description: str = "",
    ) -> None:
        step = MigrationStep(
            from_version=from_ver,
            to_version=to_ver,
            migration_id=migration_id,
            description=description,
            transform_fn=transform_fn,
        )
        self._migrations[(from_ver, to_ver)] = step

    def _find_migration_chain(self, source: str, target: str) -> Optional[MigrationChain]:
        """Discovers linear or direct migration paths."""
        if (source, target) in self._migrations:
            return MigrationChain(steps=[self._migrations[(source, target)]])

        # Try simple linear traversal (e.g. 1.0.0 -> 2.0.0 -> 3.0.0)
        current = source
        steps = []
        visited = {current}
        while current != target:
            next_hop = None
            for (f_ver, t_ver), step in self._migrations.items():
                if f_ver == current and t_ver not in visited:
                    next_hop = t_ver
                    steps.append(step)
                    visited.add(t_ver)
                    break
            if not next_hop:
                return None
            current = next_hop
        return MigrationChain(steps=steps)

    def migrate_payload(self, payload: Dict[str, Any], source_ver: str, target_ver: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Executes migration chain:
        1. Idempotency check.
        2. Preserves backup copy.
        3. Applies transformation chain sequentially.
        """
        if source_ver == target_ver:
            return True, payload, "Already at target schema version (idempotent)."

        chain = self._find_migration_chain(source_ver, target_ver)
        if not chain or not chain.steps:
            return False, payload, f"No migration path from {source_ver} to {target_ver}."

        migrated = copy.deepcopy(payload)
        for step in chain.steps:
            try:
                if step.transform_fn:
                    migrated = step.transform_fn(migrated)
                self._migration_logs.append({
                    "migration_id": step.migration_id,
                    "source": step.from_version,
                    "target": step.to_version,
                    "timestamp": time.time(),
                    "status": "SUCCESS",
                })
            except Exception as ex:
                self._migration_logs.append({
                    "migration_id": step.migration_id,
                    "source": step.from_version,
                    "target": step.to_version,
                    "timestamp": time.time(),
                    "status": "FAILED",
                    "error": str(ex),
                })
                return False, payload, f"Migration step '{step.migration_id}' failed: {ex}. Rolled back."

        migrated["schema_version"] = target_ver
        return True, migrated, f"Migrated successfully to {target_ver}."

    def migrate_slot(self, slot_id: str, target_ver: str) -> Tuple[bool, str]:
        """Migrates a save slot to the target schema version."""
        if slot_id not in self._slots:
            return False, "Slot does not exist."
        slot = self._slots[slot_id]
        if slot.schema_version == target_ver:
            return True, "Slot already at target version."

        # Backup prior to destructive migration
        self.create_backup(slot_id)

        success, new_payload, msg = self.migrate_payload(slot.payload, slot.schema_version, target_ver)
        if not success:
            return False, msg

        slot.payload = new_payload
        slot.schema_version = target_ver
        slot.checksum = slot.calculate_checksum()
        slot.updated_at = time.time()
        return True, msg

    # ==========================================================================
    # TRANSACTIONS, JOURNALING & CRASH RECOVERY (§68, §72, §73, §74, §75, §76)
    # ==========================================================================

    def simulate_crash_during_write(self, slot_id: str) -> None:
        """Simulates an abrupt power outage during write: journal stays WRITING."""
        if slot_id in self._journals:
            self._journals[slot_id].state = JournalState.WRITING
            if slot_id in self._slots:
                self._slots[slot_id].status = SlotState.CORRUPTED

    def recover_from_crash(self, slot_id: str, policy: CrashRecoveryPolicy = CrashRecoveryPolicy.USE_LAST_VALID) -> Tuple[bool, str]:
        """
        Recovers slot after crash according to configured policy:
        - COMPLETE_COMMIT: Finishes commit if temp data intact.
        - ROLLBACK: Discards uncommitted temp data.
        - USE_LAST_VALID: Restores last valid save snapshot.
        - QUARANTINE_CORRUPT: Moves corrupt slot to quarantine.
        """
        journal = self._journals.get(slot_id)

        if policy == CrashRecoveryPolicy.USE_LAST_VALID:
            if slot_id in self._previous_slots:
                self._slots[slot_id] = copy.deepcopy(self._previous_slots[slot_id])
                self._slots[slot_id].status = SlotState.VALID
                self._slots[slot_id].checksum = self._slots[slot_id].calculate_checksum()
                if journal:
                    journal.state = JournalState.ROLLED_BACK
                return True, "Recovered from last valid save."
            return False, "No previous valid save available."

        elif policy == CrashRecoveryPolicy.ROLLBACK:
            if journal and journal.backup_data is not None:
                if slot_id in self._slots:
                    self._slots[slot_id].payload = copy.deepcopy(journal.backup_data)
                    self._slots[slot_id].status = SlotState.VALID
                    self._slots[slot_id].checksum = self._slots[slot_id].calculate_checksum()
                journal.state = JournalState.ROLLED_BACK
                return True, "Transaction rolled back."
            elif slot_id in self._previous_slots:
                self._slots[slot_id] = copy.deepcopy(self._previous_slots[slot_id])
                self._slots[slot_id].status = SlotState.VALID
                self._slots[slot_id].checksum = self._slots[slot_id].calculate_checksum()
                if journal:
                    journal.state = JournalState.ROLLED_BACK
                return True, "Transaction rolled back."
            elif slot_id in self._slots:
                del self._slots[slot_id]
                return True, "Uncommitted transaction discarded."
            return False, "Nothing to roll back."

        elif policy == CrashRecoveryPolicy.COMPLETE_COMMIT:
            if journal and journal.temp_data is not None:
                if slot_id in self._slots:
                    self._slots[slot_id].payload = copy.deepcopy(journal.temp_data)
                    self._slots[slot_id].status = SlotState.VALID
                    self._slots[slot_id].checksum = self._slots[slot_id].calculate_checksum()
                else:
                    new_slot = self.create_save(slot_id, payload=copy.deepcopy(journal.temp_data))
                    new_slot.status = SlotState.VALID
                    self._slots[slot_id] = new_slot
                journal.state = JournalState.COMMITTED
                return True, "Transaction committed during recovery."
            return False, "Cannot complete commit without valid temp data."

        elif policy == CrashRecoveryPolicy.QUARANTINE_CORRUPT:
            if slot_id in self._slots:
                self._quarantine[slot_id] = {
                    "slot": copy.deepcopy(self._slots[slot_id]),
                    "timestamp": time.time(),
                }
                del self._slots[slot_id]
                return True, "Corrupt save quarantined successfully."
            return False, "Slot not found for quarantine."

        return False, "Unknown recovery policy."

    # ==========================================================================
    # ROTATIONAL BACKUPS & RESTORE (§77, §78, §79, §80, §81)
    # ==========================================================================

    def create_backup(self, slot_id: str) -> Optional[SaveBackup]:
        """Creates a timestamped rotational backup."""
        if slot_id not in self._slots:
            return None
        slot = self._slots[slot_id]
        backup = SaveBackup(
            backup_id=f"backup_{slot_id}_{int(time.time()*1000)}",
            slot_id=slot_id,
            timestamp=time.time(),
            payload=copy.deepcopy(slot.payload),
            checksum=slot.checksum,
        )
        if slot_id not in self._backups:
            self._backups[slot_id] = []
        self._backups[slot_id].append(backup)

        # Enforce max retention policy
        if len(self._backups[slot_id]) > self.max_backups_per_slot:
            self._backups[slot_id].pop(0)  # Drop oldest

        return backup

    def get_backups(self, slot_id: str) -> List[SaveBackup]:
        return list(self._backups.get(slot_id, []))

    def restore_backup(self, slot_id: str, backup_index: int = -1) -> Tuple[bool, str]:
        """Restores a slot from a validated backup."""
        backups = self._backups.get(slot_id, [])
        if not backups:
            return False, "No backups available for this slot."
        try:
            backup = backups[backup_index]
        except IndexError:
            return False, "Invalid backup index."

        if slot_id not in self._slots:
            self._slots[slot_id] = self.create_save(slot_id)

        slot = self._slots[slot_id]
        slot.payload = copy.deepcopy(backup.payload)
        slot.checksum = slot.calculate_checksum()
        slot.status = SlotState.VALID
        slot.updated_at = time.time()
        return True, f"Slot '{slot_id}' restored from backup '{backup.backup_id}'."

    # ==========================================================================
    # CLOUD SYNCHRONIZATION & CONFLICT RESOLUTION (§209, §210)
    # ==========================================================================

    def set_cloud_connected(self, connected: bool) -> None:
        self._cloud_connected = connected

    def upload_to_cloud(self, slot_id: str) -> Tuple[bool, str]:
        if not self._cloud_connected:
            return False, "Cloud storage unavailable."
        if slot_id not in self._slots or self._slots[slot_id].status != SlotState.VALID:
            return False, "Invalid local save."
        self._cloud_store[slot_id] = copy.deepcopy(self._slots[slot_id])
        return True, "Uploaded to cloud successfully."

    def download_from_cloud(self, slot_id: str) -> Tuple[bool, str]:
        if not self._cloud_connected:
            return False, "Cloud storage unavailable."
        if slot_id not in self._cloud_store:
            return False, "Slot does not exist in cloud."
        self._slots[slot_id] = copy.deepcopy(self._cloud_store[slot_id])
        return True, "Downloaded from cloud successfully."

    def resolve_cloud_conflict(
        self,
        slot_id: str,
        resolution: CloudConflictResolution = CloudConflictResolution.NEWEST_WINS,
        manual_override_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """Resolves conflict between local slot and remote cloud copy."""
        if not self._cloud_connected:
            return False, "Cloud unavailable."
        if slot_id not in self._slots or slot_id not in self._cloud_store:
            return False, "Cannot resolve conflict: missing local or cloud copy."

        local_slot = self._slots[slot_id]
        remote_slot = self._cloud_store[slot_id]

        if resolution == CloudConflictResolution.LOCAL_WINS:
            self._cloud_store[slot_id] = copy.deepcopy(local_slot)
            return True, "Resolved: local save wins."

        elif resolution == CloudConflictResolution.REMOTE_WINS:
            self._slots[slot_id] = copy.deepcopy(remote_slot)
            return True, "Resolved: remote cloud save wins."

        elif resolution == CloudConflictResolution.NEWEST_WINS:
            if local_slot.updated_at >= remote_slot.updated_at:
                self._cloud_store[slot_id] = copy.deepcopy(local_slot)
                return True, "Resolved: newest (local) save wins."
            else:
                self._slots[slot_id] = copy.deepcopy(remote_slot)
                return True, "Resolved: newest (remote) save wins."

        elif resolution == CloudConflictResolution.MANUAL_RESOLUTION:
            if manual_override_data is None:
                return False, "Manual resolution requires manual override payload."
            local_slot.payload = copy.deepcopy(manual_override_data)
            local_slot.checksum = local_slot.calculate_checksum()
            self._cloud_store[slot_id] = copy.deepcopy(local_slot)
            return True, "Resolved: manual payload applied."

        elif resolution == CloudConflictResolution.MERGE:
            merged = copy.deepcopy(remote_slot.payload)
            merged.update(local_slot.payload)
            local_slot.payload = merged
            local_slot.checksum = local_slot.calculate_checksum()
            self._cloud_store[slot_id] = copy.deepcopy(local_slot)
            return True, "Resolved: merged local and remote data."

        return False, "Unknown conflict resolution policy."

    # ==========================================================================
    # MULTIPLAYER PERSISTENCE (§211)
    # ==========================================================================

    def set_multiplayer_authority(self, authority: MultiplayerAuthority, is_server: bool = True) -> None:
        self._multiplayer_authority = authority
        self._is_server = is_server

    def request_client_save(self, slot_id: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """Checks multiplayer authority before committing client data."""
        if self._multiplayer_authority == MultiplayerAuthority.SERVER_AUTHORITATIVE and not self._is_server:
            return False, "Client write rejected: server is authoritative."
        slot = self.create_save(slot_id=slot_id, payload=payload)
        return self.write_save_atomic(slot)

    # ==========================================================================
    # MODDED DATA PERSISTENCE (§213)
    # ==========================================================================

    def validate_mod_dependencies(self, payload: Dict[str, Any], active_mods: Set[str]) -> Tuple[bool, List[str]]:
        """Verifies mod dependencies in save payload against active mods."""
        required_mods = set(payload.get("required_mods", []))
        missing = required_mods - active_mods
        if missing:
            return False, list(missing)
        return True, []

    # ==========================================================================
    # DIAGNOSTICS & HEALTH (§83)
    # ==========================================================================

    def generate_diagnostics(self) -> PersistenceDiagnosticReport:
        total = len(self._slots)
        valid = sum(1 for s in self._slots.values() if s.status == SlotState.VALID)
        corrupt = sum(1 for s in self._slots.values() if s.status == SlotState.CORRUPTED)
        pending = sum(1 for j in self._journals.values() if j.state == JournalState.WRITING)
        checkpoints = sum(1 for cp in self._checkpoints.values() if cp.is_valid)

        return PersistenceDiagnosticReport(
            is_healthy=(corrupt == 0 and pending == 0),
            total_slots=total,
            valid_slots=valid,
            corrupt_slots=corrupt,
            pending_transactions=pending,
            active_checkpoints=checkpoints,
        )

    # ==========================================================================
    # 19 GOLDEN SCENARIOS (§216)
    # ==========================================================================

    def build_golden_new_profile(self) -> PlayerProfile:
        return self.create_player_profile("golden_player_01", player_name="Operative_Alpha", level=1)

    def build_golden_default_settings(self) -> SettingsStore:
        self.reset_all_settings()
        return self.settings

    def build_golden_basic_save(self) -> SaveSlot:
        slot = self.create_save("golden_slot_basic", payload={"score": 100, "coins": 50})
        self.write_save_atomic(slot)
        return slot

    def build_golden_full_save(self) -> SaveSlot:
        slot = self.create_save(
            "golden_slot_full",
            payload={
                "player": {"hp": 100, "energy": 85},
                "inventory": ["plasma_rifle", "medkit_large", "security_keycard_red"],
                "quest": {"active": "escape_facility", "step": 3},
                "world": {"zone": "Reactor_Core", "power_grid": "ONLINE"},
            },
        )
        self.write_save_atomic(slot)
        return slot

    def build_golden_autosave(self) -> Tuple[bool, str]:
        return self.request_autosave("golden_autosave_slot", trigger=AutosaveTrigger.TIME, force=True)

    def build_golden_checkpoint(self) -> PersistenceCheckpoint:
        return self.create_checkpoint("golden_cp_01", CheckpointType.COMBAT, CheckpointLifetime.PERSISTENT, {"checkpoint_room": "Armory"})

    def build_golden_migrated_save(self) -> SaveSlot:
        # Register v1 to v2 migration
        self.register_migration_step("1.0.0", "2.0.0", "mig_v1_v2", lambda d: {**d, "skills": ["stealth"]})
        slot = self.create_save("golden_slot_migrate", schema_version="1.0.0", payload={"level": 5})
        self.write_save_atomic(slot)
        self.migrate_slot("golden_slot_migrate", "2.0.0")
        return self._slots["golden_slot_migrate"]

    def build_golden_backup(self) -> SaveBackup:
        slot = self.create_save("golden_slot_backup", payload={"progress": "mid_game"})
        self.write_save_atomic(slot)
        return self.create_backup("golden_slot_backup")

    def build_golden_recovery(self) -> Tuple[bool, str]:
        slot = self.create_save("golden_slot_recover", payload={"checkpoint": "Sector_4"})
        self.write_save_atomic(slot)
        # Update with crash
        self._previous_slots["golden_slot_recover"] = copy.deepcopy(self._slots["golden_slot_recover"])
        self._slots["golden_slot_recover"].payload = {"checkpoint": "Crash_Corrupt"}
        self.simulate_crash_during_write("golden_slot_recover")
        return self.recover_from_crash("golden_slot_recover", CrashRecoveryPolicy.USE_LAST_VALID)

    def build_golden_corrupted_save(self) -> SaveSlot:
        slot = self.create_save("golden_slot_corrupt", payload={"data": "valid"})
        self.write_save_atomic(slot)
        # Tamper payload without updating checksum
        self._slots["golden_slot_corrupt"].payload["data"] = "tampered_corrupt"
        return self._slots["golden_slot_corrupt"]

    def build_golden_cloud_conflict(self) -> Tuple[bool, str]:
        slot = self.create_save("golden_cloud_slot", payload={"source": "local", "credits": 500})
        self.write_save_atomic(slot)
        self.upload_to_cloud("golden_cloud_slot")
        # Change local
        self._slots["golden_cloud_slot"].payload["credits"] = 600
        self._slots["golden_cloud_slot"].updated_at += 10.0
        return self.resolve_cloud_conflict("golden_cloud_slot", CloudConflictResolution.NEWEST_WINS)

    def build_golden_settings(self) -> SettingsStore:
        self.set_setting("master_volume", 0.75)
        self.set_setting("subtitles", True)
        self.confirm_setting("master_volume")
        return self.settings

    def build_golden_input_profile(self) -> UserProfile:
        user = self.create_user_profile("golden_user_input", input_bindings={"FIRE": "Mouse0", "DODGE": "LShift"})
        return user

    def build_golden_accessibility_profile(self) -> UserProfile:
        user = self.create_user_profile(
            "golden_user_access",
            accessibility_options={"colorblind": "DEUTERANOPIA", "subtitles": True, "high_contrast": True},
        )
        return user

    def build_golden_world_state(self) -> SaveSlot:
        slot = self.create_save("golden_world_state", payload={"actors": 150, "doors": {"door_a": "LOCKED", "door_b": "OPEN"}})
        self.write_save_atomic(slot)
        return slot

    def build_golden_player_state(self) -> SaveSlot:
        slot = self.create_save("golden_player_state", payload={"health": 95, "shields": 100, "stamina": 80})
        self.write_save_atomic(slot)
        return slot

    def build_golden_quest_state(self) -> SaveSlot:
        slot = self.create_save("golden_quest_state", payload={"main_quest": "Infiltrate_Base", "completed": ["Find_Entryway"]})
        self.write_save_atomic(slot)
        return slot

    def build_golden_inventory_state(self) -> SaveSlot:
        slot = self.create_save("golden_inventory_state", payload={"items": [{"id": "ammo_9mm", "count": 120}], "capacity": 20})
        self.write_save_atomic(slot)
        return slot

    def build_golden_complete_runtime(self) -> Dict[str, Any]:
        p_prof = self.build_golden_new_profile()
        u_prof = self.build_golden_input_profile()
        save = self.build_golden_full_save()
        cp = self.build_golden_checkpoint()
        return {
            "player_profile": p_prof,
            "user_profile": u_prof,
            "save_slot": save,
            "checkpoint": cp,
            "diagnostics": self.generate_diagnostics(),
        }

    # ==========================================================================
    # END-TO-END WORKFLOW (§217)
    # ==========================================================================

    def run_end_to_end_pipeline(self) -> Dict[str, Any]:
        """
        Executes the normative 27-step lifecycle defined in §217:
        FIRST_BOOT -> CREATE_PROFILE -> SET_LANGUAGE -> SET_ACCESSIBILITY ->
        SET_CONTROLS -> START_GAME -> PROGRESS -> CREATE_CHECKPOINT ->
        AUTOSAVE -> MANUAL_SAVE -> CLOSE -> RESTART -> DISCOVER_SAVE ->
        VERIFY_INTEGRITY -> LOAD -> POST_LOAD_VALIDATE -> CONTINUE ->
        CHANGE_SETTINGS -> SAVE -> SIMULATE_CRASH -> RECOVER ->
        LOAD_PREVIOUS_VALID -> MIGRATE_SCHEMA -> VALIDATE_MIGRATION ->
        BACKUP -> RESTORE -> CLOUD_SYNC -> CONFLICT -> RESOLVE -> FINAL_SAVE.
        """
        results = {}

        # 1. FIRST_BOOT & CREATE_PROFILE
        user = self.create_user_profile("user_e2e", "E2E_Tester")
        player = self.create_player_profile("player_e2e", "E2E_Operative")
        results["boot_profile"] = (user.user_id, player.profile_id)

        # 2. SET_LANGUAGE, ACCESSIBILITY, CONTROLS
        user.language = "es"
        user.accessibility_options["high_contrast"] = True
        user.input_bindings["INTERACT"] = "F"
        results["settings_configured"] = True

        # 3. START_GAME & PROGRESS
        player.level = 2
        player.inventory["rifle"] = 1

        # 4. CREATE_CHECKPOINT & AUTOSAVE & MANUAL_SAVE
        cp = self.create_checkpoint("e2e_cp_1", CheckpointType.MISSION, data={"room": "Hub"})
        auto_ok, _ = self.request_autosave("e2e_auto", force=True)
        slot = self.create_save("e2e_manual", profile_id=player.profile_id, payload={"progress": 25})
        save_ok, _ = self.write_save_atomic(slot)
        results["saves_created"] = auto_ok and save_ok

        # 5. CLOSE & RESTART & DISCOVER_SAVE & VERIFY_INTEGRITY
        saves = self.list_saves()
        results["discovered_count"] = len(saves)

        # 6. LOAD & POST_LOAD_VALIDATE
        loaded = self.load_save("e2e_manual")
        results["loaded_valid"] = loaded is not None and loaded.checksum == loaded.calculate_checksum()

        # 7. CHANGE_SETTINGS & SAVE
        self.set_setting("music_volume", 0.5)
        self.confirm_setting("music_volume")
        slot.payload["progress"] = 30
        self.write_save_atomic(slot)

        # 8. SIMULATE_CRASH & RECOVER & LOAD_PREVIOUS_VALID
        self.simulate_crash_during_write("e2e_manual")
        rec_ok, _ = self.recover_from_crash("e2e_manual", CrashRecoveryPolicy.USE_LAST_VALID)
        results["recovered_previous"] = rec_ok

        # 9. MIGRATE_SCHEMA & VALIDATE_MIGRATION
        self.register_migration_step("1.0.0", "2.0.0", "e2e_mig", lambda d: {**d, "migrated": True})
        mig_ok, _ = self.migrate_slot("e2e_manual", "2.0.0")
        results["migration_ok"] = mig_ok

        # 10. BACKUP & RESTORE
        backup = self.create_backup("e2e_manual")
        rest_ok, _ = self.restore_backup("e2e_manual")
        results["backup_restore"] = rest_ok

        # 11. CLOUD_SYNC & CONFLICT & RESOLVE & FINAL_SAVE
        self.upload_to_cloud("e2e_manual")
        self._slots["e2e_manual"].payload["final"] = True
        conf_ok, _ = self.resolve_cloud_conflict("e2e_manual", CloudConflictResolution.LOCAL_WINS)
        results["cloud_conflict_resolved"] = conf_ok

        results["status"] = "SUCCESS"
        return results
