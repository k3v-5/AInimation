import sqlite3
import json
from typing import List, Optional, Dict, Any
from ..core.memory_schema import FailureRecord, CorrectionRecord, StrategyRecord

class SQLiteMemoryStore:
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
                CREATE TABLE IF NOT EXISTS failures (
                    failure_id TEXT PRIMARY KEY,
                    asset_id TEXT,
                    asset_type TEXT,
                    component_type TEXT,
                    failure_type TEXT,
                    metric TEXT,
                    actual_value REAL,
                    expected_value REAL,
                    severity TEXT,
                    fingerprint TEXT,
                    timestamp REAL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS corrections (
                    correction_id TEXT PRIMARY KEY,
                    failure_id TEXT,
                    strategy_id TEXT,
                    operation_type TEXT,
                    target TEXT,
                    parameters_json TEXT,
                    before_score REAL,
                    after_score REAL,
                    result TEXT,
                    is_rollback INTEGER,
                    timestamp REAL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    strategy_id TEXT PRIMARY KEY,
                    failure_type TEXT,
                    asset_type TEXT,
                    component_type TEXT,
                    preferred_operation TEXT,
                    parameters_json TEXT,
                    sample_count INTEGER,
                    success_count INTEGER,
                    failure_count INTEGER,
                    success_rate REAL,
                    confidence REAL,
                    average_improvement REAL,
                    engine_version TEXT
                )
            """)

    def store_failure(self, rec: FailureRecord):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO failures 
                (failure_id, asset_id, asset_type, component_type, failure_type, metric, actual_value, expected_value, severity, fingerprint, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rec.failure_id, rec.asset_id, rec.asset_type, rec.component_type, rec.failure_type, rec.metric, rec.actual_value, rec.expected_value, rec.severity, rec.fingerprint, rec.timestamp))

    def store_correction(self, rec: CorrectionRecord):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO corrections
                (correction_id, failure_id, strategy_id, operation_type, target, parameters_json, before_score, after_score, result, is_rollback, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rec.correction_id, rec.failure_id, rec.strategy_id, rec.operation_type, rec.target, json.dumps(rec.parameters), rec.before_score, rec.after_score, rec.result, 1 if rec.is_rollback else 0, rec.timestamp))

    def store_strategy(self, rec: StrategyRecord):
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO strategies
                (strategy_id, failure_type, asset_type, component_type, preferred_operation, parameters_json, sample_count, success_count, failure_count, success_rate, confidence, average_improvement, engine_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rec.strategy_id, rec.failure_type, rec.asset_type, rec.component_type, rec.preferred_operation, json.dumps(rec.parameters), rec.sample_count, rec.success_count, rec.failure_count, rec.success_rate, rec.confidence, rec.average_improvement, rec.engine_version))

    def get_strategy(self, strategy_id: str) -> Optional[StrategyRecord]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM strategies WHERE strategy_id = ?", (strategy_id,))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_strategy(row)

    def find_strategies(self, failure_type: str, asset_type: Optional[str] = None) -> List[StrategyRecord]:
        cur = self.conn.cursor()
        if asset_type:
            cur.execute("SELECT * FROM strategies WHERE failure_type = ? AND asset_type = ?", (failure_type, asset_type))
        else:
            cur.execute("SELECT * FROM strategies WHERE failure_type = ?", (failure_type,))
        rows = cur.fetchall()
        return [self._row_to_strategy(r) for r in rows]

    def count_failures_by_type(self, failure_type: str, asset_type: str) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM failures WHERE failure_type = ? AND asset_type = ?", (failure_type, asset_type))
        return cur.fetchone()[0]

    def _row_to_strategy(self, row: sqlite3.Row) -> StrategyRecord:
        return StrategyRecord(
            strategy_id=row["strategy_id"],
            failure_type=row["failure_type"],
            asset_type=row["asset_type"],
            component_type=row["component_type"],
            preferred_operation=row["preferred_operation"],
            parameters=json.loads(row["parameters_json"]),
            sample_count=row["sample_count"],
            success_count=row["success_count"],
            failure_count=row["failure_count"],
            success_rate=row["success_rate"],
            confidence=row["confidence"],
            average_improvement=row["average_improvement"],
            engine_version=row["engine_version"]
        )
