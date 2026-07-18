"""SQLite database layer for persistence and caching."""
import sqlite3
import json
import time
import threading
from typing import Any, Optional

class Database:
    """Thread-safe SQLite database with TTL cache."""
    
    def __init__(self, db_path: str = "stadiumiq.db"):
        self._local = threading.local()
        self._db_path = db_path
        self._init_db()
    
    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self._db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _init_db(self):
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS fan_journeys (
                fan_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sentiment_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                sentiment TEXT,
                score REAL,
                created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS match_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                event TEXT,
                minute INTEGER,
                created_at REAL NOT NULL
            );
        """)
        conn.commit()
    
    def cache_get(self, key: str) -> Optional[Any]:
        conn = self._get_conn()
        row = conn.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,)).fetchone()
        if row and row['expires_at'] > time.time():
            return json.loads(row['value'])
        if row:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
        return None
    
    def cache_set(self, key: str, value: Any, ttl: float = 5.0):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value, default=str), time.time() + ttl)
        )
        conn.commit()
    
    def cache_clear(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM cache WHERE expires_at <= ?", (time.time(),))
        conn.commit()
    
    def save_fan_journey(self, fan_id: str, data: dict):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO fan_journeys (fan_id, data, updated_at) VALUES (?, ?, ?)",
            (fan_id, json.dumps(data, default=str), time.time())
        )
        conn.commit()
    
    def get_fan_journey(self, fan_id: str) -> Optional[dict]:
        conn = self._get_conn()
        row = conn.execute("SELECT data FROM fan_journeys WHERE fan_id = ?", (fan_id,)).fetchone()
        return json.loads(row['data']) if row else None
    
    def save_incident(self, incident_id: str, data: dict):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO incidents (id, data, created_at) VALUES (?, ?, ?)",
            (incident_id, json.dumps(data, default=str), time.time())
        )
        conn.commit()
    
    def save_sentiment(self, text: str, sentiment: str, score: float):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO sentiment_log (text, sentiment, score, created_at) VALUES (?, ?, ?, ?)",
            (text, sentiment, score, time.time())
        )
        conn.commit()

    def save_match_event(self, match_id: str, event: dict):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO match_events (match_id, event, minute, created_at) VALUES (?, ?, ?, ?)",
            (match_id, json.dumps(event, default=str), event.get("minute", 0), time.time())
        )
        conn.commit()
    
    def get_sentiment_count(self, sentiment: str) -> int:
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM sentiment_log WHERE sentiment = ?", (sentiment,)).fetchone()
        return row['cnt'] if row else 0
    
    def get_total_sentiments(self) -> int:
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM sentiment_log").fetchone()
        return row['cnt'] if row else 0
    
    def cleanup(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM cache WHERE expires_at <= ?", (time.time(),))
        conn.commit()

db = Database()
