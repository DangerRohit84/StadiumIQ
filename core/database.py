"""SQLite database layer for persistence and caching."""
import sqlite3
import json
import time
import threading
from contextlib import contextmanager
from typing import Any, Optional

MAX_CACHE_ROWS = 10000
MAX_SENTIMENT_ROWS = 5000
MAX_MATCH_EVENT_ROWS = 5000
MAX_RETRIES = 3
RETRY_DELAY = 0.05


class Database:
    """Thread-safe SQLite database with TTL cache."""

    def __init__(self, db_path: str = "stadiumiq.db") -> None:
        """Initialize the database with the given path."""
        self._local = threading.local()
        self._db_path = db_path
        self._query_count = 0
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Return a thread-safe database connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self._db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA cache_size=-64000")
            self._local.conn.execute("PRAGMA busy_timeout=30000")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
        self._query_count += 1
        return self._local.conn

    @contextmanager
    def _transaction(self):
        """Context manager for atomic database transactions."""
        conn = self._get_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    @property
    def _dirty(self) -> bool:
        """Return the per-thread dirty flag."""
        return getattr(self._local, '_dirty', False)

    @_dirty.setter
    def _dirty(self, value: bool) -> None:
        """Set the per-thread dirty flag."""
        self._local._dirty = value

    def health_check(self) -> bool:
        """Verify database connection is alive."""
        try:
            conn = self._get_conn()
            conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def _init_db(self) -> None:
        """Initialize database schema and pragmas."""
        conn = self._get_conn()
        conn.execute("PRAGMA foreign_keys=ON")
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
            CREATE INDEX IF NOT EXISTS idx_sentiment_sentiment ON sentiment_log(sentiment);
            CREATE TABLE IF NOT EXISTS match_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                event TEXT,
                minute INTEGER,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_match_events_match_id ON match_events(match_id);
            CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at);
            CREATE INDEX IF NOT EXISTS idx_sentiment_created ON sentiment_log(created_at);
            CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents(created_at);
            CREATE INDEX IF NOT EXISTS idx_match_created ON match_events(created_at);
            CREATE INDEX IF NOT EXISTS idx_sentiment_sentiment_created ON sentiment_log(sentiment, created_at);
        """)
        conn.commit()
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache if not expired."""
        conn = self._get_conn()
        row = conn.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,)).fetchone()
        if row and row['expires_at'] > time.time():
            return json.loads(row['value'])
        return None

    def cache_set(self, key: str, value: Any, ttl: float = 5.0) -> None:
        """Store a value in cache with a time-to-live."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self._get_conn()
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                    (key, json.dumps(value, default=str), time.time() + ttl)
                )
                self._dirty = True
                row_count = conn.execute("SELECT COUNT(*) as cnt FROM cache").fetchone()['cnt']
                if row_count > MAX_CACHE_ROWS:
                    conn.execute("DELETE FROM cache WHERE expires_at <= ?", (time.time(),))
                return
            except sqlite3.OperationalError:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise
    
    def cache_clear(self) -> None:
        """Delete expired cache entries."""
        self.flush()
        conn = self._get_conn()
        conn.execute("DELETE FROM cache WHERE expires_at <= ?", (time.time(),))
        conn.commit()

    def cache_flush(self) -> None:
        """Delete ALL cache entries including valid ones (for testing)."""
        self.flush()
        conn = self._get_conn()
        conn.execute("DELETE FROM cache")
        conn.commit()
    
    def save_fan_journey(self, fan_id: str, data: dict) -> None:
        """Save fan journey data to the database."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self._get_conn()
                conn.execute(
                    "INSERT OR REPLACE INTO fan_journeys (fan_id, data, updated_at) VALUES (?, ?, ?)",
                    (fan_id, json.dumps(data, default=str), time.time())
                )
                self._dirty = True
                return
            except sqlite3.OperationalError:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise
    
    def get_fan_journey(self, fan_id: str) -> Optional[dict]:
        """Retrieve fan journey data from the database."""
        self.flush()
        conn = self._get_conn()
        row = conn.execute("SELECT data FROM fan_journeys WHERE fan_id = ?", (fan_id,)).fetchone()
        return json.loads(row['data']) if row else None
    
    def save_incident(self, incident_id: str, data: dict) -> None:
        """Save emergency incident data to the database."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self._get_conn()
                conn.execute(
                    "INSERT OR REPLACE INTO incidents (id, data, created_at) VALUES (?, ?, ?)",
                    (incident_id, json.dumps(data, default=str), time.time())
                )
                self._dirty = True
                return
            except sqlite3.OperationalError:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise

    def save_sentiment(self, text: str, sentiment: str, score: float) -> None:
        """Save sentiment analysis result to the database."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self._get_conn()
                conn.execute(
                    "INSERT INTO sentiment_log (text, sentiment, score, created_at) VALUES (?, ?, ?, ?)",
                    (text, sentiment, score, time.time())
                )
                self._dirty = True
                row_count = conn.execute("SELECT COUNT(*) as cnt FROM sentiment_log").fetchone()['cnt']
                if row_count > MAX_SENTIMENT_ROWS:
                    conn.execute(f"DELETE FROM sentiment_log WHERE id NOT IN (SELECT id FROM sentiment_log ORDER BY created_at DESC LIMIT {MAX_SENTIMENT_ROWS})")
                return
            except sqlite3.OperationalError:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise

    def save_match_event(self, match_id: str, event: dict) -> None:
        """Save a match event to the database."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self._get_conn()
                conn.execute(
                    "INSERT INTO match_events (match_id, event, minute, created_at) VALUES (?, ?, ?, ?)",
                    (match_id, json.dumps(event, default=str), event.get("minute", 0), time.time())
                )
                self._dirty = True
                row_count = conn.execute("SELECT COUNT(*) as cnt FROM match_events").fetchone()['cnt']
                if row_count > MAX_MATCH_EVENT_ROWS:
                    conn.execute(f"DELETE FROM match_events WHERE id NOT IN (SELECT id FROM match_events ORDER BY created_at DESC LIMIT {MAX_MATCH_EVENT_ROWS})")
                return
            except sqlite3.OperationalError:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise
    
    def get_sentiment_count(self, sentiment: str) -> int:
        """Count occurrences of a specific sentiment in the log."""
        self.flush()
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM sentiment_log WHERE sentiment = ?", (sentiment,)).fetchone()
        return row['cnt'] if row else 0
    
    def get_total_sentiments(self) -> int:
        """Return total number of sentiment records."""
        self.flush()
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM sentiment_log").fetchone()
        return row['cnt'] if row else 0
    
    def flush(self) -> None:
        """Commit pending writes."""
        if self._dirty:
            try:
                self._get_conn().commit()
            except sqlite3.OperationalError:
                pass
            self._dirty = False

    def cleanup(self) -> None:
        """Remove expired cache entries and prune old logs."""
        conn = self._get_conn()
        conn.execute("DELETE FROM cache WHERE expires_at <= ?", (time.time(),))
        conn.execute(f"DELETE FROM sentiment_log WHERE id NOT IN (SELECT id FROM sentiment_log ORDER BY created_at DESC LIMIT {MAX_SENTIMENT_ROWS})")
        conn.execute(f"DELETE FROM match_events WHERE id NOT IN (SELECT id FROM match_events ORDER BY created_at DESC LIMIT {MAX_MATCH_EVENT_ROWS})")
        conn.commit()

db = Database()
