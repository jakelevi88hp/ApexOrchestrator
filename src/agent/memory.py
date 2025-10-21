"""
Memory System for Autonomous Agent

Provides persistent memory, context management, and execution history tracking.
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger("apex_orchestrator.agent.memory")


class MemorySystem:
    """Persistent memory system for the autonomous agent"""

    def __init__(self, db_path: str = "logs/agent_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"Memory system initialized at {self.db_path}")

    def _init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Execution history
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                intent TEXT,
                plan TEXT,
                success BOOLEAN,
                execution_time_ms INTEGER,
                error_message TEXT,
                context TEXT,
                result_hash TEXT
            )
        """
        )

        # Learned patterns
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_execution_time_ms REAL,
                last_used TEXT,
                created_at TEXT,
                confidence_score REAL DEFAULT 0.5
            )
        """
        )

        # Code templates
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS code_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                code TEXT NOT NULL,
                language TEXT DEFAULT 'python',
                use_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                created_at TEXT,
                updated_at TEXT,
                tags TEXT
            )
        """
        )

        # Self-modifications log
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS modifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                modification_type TEXT NOT NULL,
                target_file TEXT,
                description TEXT,
                code_before TEXT,
                code_after TEXT,
                test_results TEXT,
                applied BOOLEAN DEFAULT 0,
                rolled_back BOOLEAN DEFAULT 0,
                reason TEXT
            )
        """
        )

        # Agent state
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """
        )

        # Performance metrics
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                context TEXT
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("Database schema initialized")

    def record_execution(
        self,
        operation_type: str,
        intent: str,
        plan: Dict,
        success: bool,
        execution_time_ms: int,
        error_message: Optional[str] = None,
        context: Optional[Dict] = None,
        result: Optional[Any] = None,
    ):
        """Record an execution in memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        result_hash = None
        if result:
            result_str = json.dumps(result, sort_keys=True)
            result_hash = hashlib.sha256(result_str.encode()).hexdigest()[:16]

        cursor.execute(
            """
            INSERT INTO executions 
            (timestamp, operation_type, intent, plan, success, execution_time_ms, 
             error_message, context, result_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.utcnow().isoformat(),
                operation_type,
                intent,
                json.dumps(plan),
                success,
                execution_time_ms,
                error_message,
                json.dumps(context) if context else None,
                result_hash,
            ),
        )

        conn.commit()
        conn.close()
        logger.info(f"Recorded execution: {operation_type} - Success: {success}")

    def get_execution_history(self, limit: int = 100, operation_type: Optional[str] = None) -> List[Dict]:
        """Retrieve execution history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM executions"
        params = []

        if operation_type:
            query += " WHERE operation_type = ?"
            params.append(operation_type)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def get_success_rate(self, operation_type: Optional[str] = None, hours: int = 24) -> float:
        """Calculate success rate for operations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT 
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                COUNT(*) as total
            FROM executions
            WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
        """
        params = [hours]

        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)

        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()

        if result and result[1] > 0:
            return result[0] / result[1]
        return 0.0

    def save_pattern(self, pattern_type: str, pattern_data: Dict, success: bool, execution_time_ms: int):
        """Save a learned pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        pattern_json = json.dumps(pattern_data, sort_keys=True)
        pattern_hash = hashlib.sha256(pattern_json.encode()).hexdigest()[:16]

        # Check if pattern exists
        cursor.execute(
            """
            SELECT id, success_count, failure_count, avg_execution_time_ms 
            FROM patterns 
            WHERE pattern_type = ? AND result_hash = ?
        """,
            (pattern_type, pattern_hash),
        )

        existing = cursor.fetchone()

        if existing:
            # Update existing pattern
            pid, succ, fail, avg_time = existing
            new_succ = succ + (1 if success else 0)
            new_fail = fail + (0 if success else 1)
            new_avg = ((avg_time or 0) * (succ + fail) + execution_time_ms) / (new_succ + new_fail)
            confidence = new_succ / (new_succ + new_fail) if (new_succ + new_fail) > 0 else 0.5

            cursor.execute(
                """
                UPDATE patterns 
                SET success_count = ?, failure_count = ?, 
                    avg_execution_time_ms = ?, last_used = ?,
                    confidence_score = ?
                WHERE id = ?
            """,
                (new_succ, new_fail, new_avg, datetime.utcnow().isoformat(), confidence, pid),
            )
        else:
            # Insert new pattern
            cursor.execute(
                """
                INSERT INTO patterns 
                (pattern_type, pattern_data, success_count, failure_count, 
                 avg_execution_time_ms, last_used, created_at, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pattern_type,
                    pattern_json,
                    1 if success else 0,
                    0 if success else 1,
                    execution_time_ms,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                    1.0 if success else 0.0,
                ),
            )

        conn.commit()
        conn.close()
        logger.info(f"Saved pattern: {pattern_type}")

    def get_best_patterns(self, pattern_type: str, limit: int = 10) -> List[Dict]:
        """Get best performing patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM patterns
            WHERE pattern_type = ?
            ORDER BY confidence_score DESC, success_count DESC
            LIMIT ?
        """,
            (pattern_type, limit),
        )

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def save_code_template(
        self, name: str, code: str, description: str = "", language: str = "python", tags: List[str] = None
    ):
        """Save a reusable code template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()
        tags_str = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT OR REPLACE INTO code_templates 
            (name, description, code, language, created_at, updated_at, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (name, description, code, language, now, now, tags_str),
        )

        conn.commit()
        conn.close()
        logger.info(f"Saved code template: {name}")

    def get_code_template(self, name: str) -> Optional[Dict]:
        """Retrieve a code template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM code_templates WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result:
            columns = [desc[0] for desc in cursor.description]
            template = dict(zip(columns, result))
            conn.close()
            return template

        conn.close()
        return None

    def record_modification(
        self,
        modification_type: str,
        target_file: str,
        description: str,
        code_before: str,
        code_after: str,
        test_results: Dict,
        applied: bool,
        reason: str = "",
    ):
        """Record a self-modification attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO modifications
            (timestamp, modification_type, target_file, description,
             code_before, code_after, test_results, applied, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.utcnow().isoformat(),
                modification_type,
                target_file,
                description,
                code_before,
                code_after,
                json.dumps(test_results),
                applied,
                reason,
            ),
        )

        conn.commit()
        conn.close()
        logger.info(f"Recorded modification: {modification_type} - Applied: {applied}")

    def get_agent_state(self, key: str) -> Optional[str]:
        """Get agent state value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM agent_state WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def set_agent_state(self, key: str, value: str):
        """Set agent state value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO agent_state (key, value, updated_at)
            VALUES (?, ?, ?)
        """,
            (key, value, datetime.utcnow().isoformat()),
        )

        conn.commit()
        conn.close()

    def record_metric(self, metric_name: str, metric_value: float, context: Optional[Dict] = None):
        """Record a performance metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO metrics (timestamp, metric_name, metric_value, context)
            VALUES (?, ?, ?, ?)
        """,
            (datetime.utcnow().isoformat(), metric_name, metric_value, json.dumps(context) if context else None),
        )

        conn.commit()
        conn.close()

    def get_metrics(self, metric_name: str, hours: int = 24) -> List[Dict]:
        """Get metrics for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM metrics
            WHERE metric_name = ?
            AND datetime(timestamp) > datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        """,
            (metric_name, hours),
        )

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total executions
        cursor.execute("SELECT COUNT(*) FROM executions")
        stats["total_executions"] = cursor.fetchone()[0]

        # Success rate
        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
            FROM executions
        """
        )
        stats["overall_success_rate"] = cursor.fetchone()[0] or 0.0

        # Learned patterns
        cursor.execute("SELECT COUNT(*) FROM patterns")
        stats["learned_patterns"] = cursor.fetchone()[0]

        # Code templates
        cursor.execute("SELECT COUNT(*) FROM code_templates")
        stats["code_templates"] = cursor.fetchone()[0]

        # Modifications
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN applied = 1 THEN 1 ELSE 0 END) as applied
            FROM modifications
        """
        )
        mod_result = cursor.fetchone()
        stats["total_modifications"] = mod_result[0]
        stats["applied_modifications"] = mod_result[1] or 0

        conn.close()
        return stats
