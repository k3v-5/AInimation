import sqlite3
import json
from typing import List, Optional, Dict, Any
from ..core.memory_schema import (
    AssetRecord, AssetVersionRecord, PatternRecord, PatternEvidence,
    EvaluationRecord, FailureMemoryRecord, AuditEvent
)
from ..core.memory_status import AssetStatus, PatternStatus, PatternScope

class SQLiteAssetStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def close(self):
        if self.conn:
            self.conn.close()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    name TEXT,
                    asset_type TEXT,
                    template_id TEXT,
                    status TEXT,
                    created_at REAL,
                    updated_at REAL,
                    tags_json TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS asset_versions (
                    version_id TEXT PRIMARY KEY,
                    asset_id TEXT,
                    version_number TEXT,
                    parent_version_id TEXT,
                    branch TEXT,
                    parameters_json TEXT,
                    parameter_hash TEXT,
                    template_version TEXT,
                    generation_seed INTEGER,
                    created_at REAL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    template_id TEXT,
                    trigger_issue TEXT,
                    recommended_action TEXT,
                    target_parameter TEXT,
                    parameter_multiplier REAL,
                    status TEXT,
                    scope TEXT,
                    confidence REAL,
                    evidence_count INTEGER,
                    success_count INTEGER,
                    failure_count INTEGER,
                    success_rate REAL,
                    compatible_template_versions TEXT,
                    created_at REAL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_evidence (
                    evidence_id TEXT PRIMARY KEY,
                    pattern_id TEXT,
                    asset_id TEXT,
                    version_id TEXT,
                    before_score REAL,
                    after_score REAL,
                    result TEXT,
                    timestamp REAL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS failures (
                    failure_id TEXT PRIMARY KEY,
                    asset_id TEXT,
                    template_id TEXT,
                    problematic_parameters_json TEXT,
                    error_type TEXT,
                    created_at REAL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    entity_id TEXT,
                    entity_type TEXT,
                    event_type TEXT,
                    actor TEXT,
                    payload_hash TEXT,
                    timestamp REAL
                )
            """)

    def store_asset(self, rec: AssetRecord):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO assets
                (asset_id, name, asset_type, template_id, status, created_at, updated_at, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (rec.asset_id, rec.name, rec.asset_type, rec.template_id, rec.status.value, rec.created_at, rec.updated_at, json.dumps(rec.tags)))

    def store_version(self, rec: AssetVersionRecord):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO asset_versions
                (version_id, asset_id, version_number, parent_version_id, branch, parameters_json, parameter_hash, template_version, generation_seed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rec.version_id, rec.asset_id, rec.version_number, rec.parent_version_id, rec.branch, json.dumps(rec.parameters), rec.parameter_hash, rec.template_version, rec.generation_seed, rec.created_at))

    def find_version_by_hash(self, asset_id: str, parameter_hash: str) -> Optional[AssetVersionRecord]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM asset_versions WHERE asset_id = ? AND parameter_hash = ?", (asset_id, parameter_hash))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_version(row)

    def store_pattern(self, rec: PatternRecord):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO patterns
                (pattern_id, template_id, trigger_issue, recommended_action, target_parameter, parameter_multiplier, status, scope, confidence, evidence_count, success_count, failure_count, success_rate, compatible_template_versions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rec.pattern_id, rec.template_id, rec.trigger_issue, rec.recommended_action, rec.target_parameter, rec.parameter_multiplier, rec.status.value, rec.scope.value, rec.confidence, rec.evidence_count, rec.success_count, rec.failure_count, rec.success_rate, rec.compatible_template_versions, rec.created_at))

    def get_pattern(self, pattern_id: str) -> Optional[PatternRecord]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM patterns WHERE pattern_id = ?", (pattern_id,))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_pattern(row)

    def find_patterns(self, template_id: str, trigger_issue: Optional[str] = None) -> List[PatternRecord]:
        cur = self.conn.cursor()
        if trigger_issue:
            cur.execute("SELECT * FROM patterns WHERE template_id = ? AND trigger_issue = ?", (template_id, trigger_issue))
        else:
            cur.execute("SELECT * FROM patterns WHERE template_id = ?", (template_id,))
        rows = cur.fetchall()
        return [self._row_to_pattern(r) for r in rows]

    def store_failure(self, rec: FailureMemoryRecord):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO failures
                (failure_id, asset_id, template_id, problematic_parameters_json, error_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (rec.failure_id, rec.asset_id, rec.template_id, json.dumps(rec.problematic_parameters), rec.error_type, rec.created_at))

    def get_failures(self, template_id: str) -> List[FailureMemoryRecord]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM failures WHERE template_id = ?", (template_id,))
        rows = cur.fetchall()
        return [FailureMemoryRecord(
            failure_id=r["failure_id"],
            asset_id=r["asset_id"],
            template_id=r["template_id"],
            problematic_parameters=json.loads(r["problematic_parameters_json"]),
            error_type=r["error_type"],
            created_at=r["created_at"]
        ) for r in rows]

    def store_event(self, rec: AuditEvent):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO events
                (event_id, entity_id, entity_type, event_type, actor, payload_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (rec.event_id, rec.entity_id, rec.entity_type, rec.event_type, rec.actor, rec.payload_hash, rec.timestamp))

    def _row_to_version(self, row: sqlite3.Row) -> AssetVersionRecord:
        return AssetVersionRecord(
            version_id=row["version_id"],
            asset_id=row["asset_id"],
            version_number=row["version_number"],
            parent_version_id=row["parent_version_id"],
            branch=row["branch"],
            parameters=json.loads(row["parameters_json"]),
            parameter_hash=row["parameter_hash"],
            template_version=row["template_version"],
            generation_seed=row["generation_seed"],
            created_at=row["created_at"]
        )

    def _row_to_pattern(self, row: sqlite3.Row) -> PatternRecord:
        return PatternRecord(
            pattern_id=row["pattern_id"],
            template_id=row["template_id"],
            trigger_issue=row["trigger_issue"],
            recommended_action=row["recommended_action"],
            target_parameter=row["target_parameter"],
            parameter_multiplier=row["parameter_multiplier"],
            status=PatternStatus(row["status"]),
            scope=PatternScope(row["scope"]),
            confidence=row["confidence"],
            evidence_count=row["evidence_count"],
            success_count=row["success_count"],
            failure_count=row["failure_count"],
            success_rate=row["success_rate"],
            compatible_template_versions=row["compatible_template_versions"],
            created_at=row["created_at"]
        )
