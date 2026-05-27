import sqlite3
import hashlib
import json
from datetime import datetime

class AuditDatabase:
    def __init__(self, db_path="election_assistant_audit.db"):
        self.db_path = db_path
        self.initialize_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Table tracking historical dialogue strings safely
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table processing administrative audits with data hashes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_audit_ledger (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_summary TEXT,
                    cryptographic_integrity_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def store_chat_turn(self, session_id: str, role: str, content: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()
        self.write_audit_log(session_id, "CHAT_TURN_STORED", {"role": role, "content_length": len(content)})

    def fetch_chat_history(self, session_id: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            rows = cursor.fetchall()
            return [{"role": row["role"], "text": row["content"]} for row in rows]

    def clear_session_history(self, session_id: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()
        self.write_audit_log(session_id, "SESSION_HISTORY_PURGED", {"target_session": session_id})

    def write_audit_log(self, session_id: str, event_type: str, payload: dict):
        payload_str = json.dumps(payload)
        raw_token = f"{datetime.utcnow().isoformat()}-{session_id}-{event_type}-{payload_str}"
        computed_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO security_audit_ledger 
                (session_id, event_type, payload_summary, cryptographic_integrity_hash)
                VALUES (?, ?, ?, ?)
            """, (session_id, event_type, payload_str, computed_hash))
            conn.commit()