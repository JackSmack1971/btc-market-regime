import sqlite3
import pickle
from pathlib import Path
from datetime import datetime
from typing import Any, Optional, Dict, List
from ..utils import logger

class DatabaseManager:
    """Manages SQLite persistence for market intelligence data."""
    
    def __init__(self, db_path: str = "data/market_regime.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initializes the database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    value REAL,
                    timestamp DATETIME,
                    source TEXT,
                    UNIQUE(metric_name, timestamp)
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully", path=str(self.db_path))

    def set_cache(self, key: str, value: Any):
        """Stores a pickled value in the cache table."""
        serialized = pickle.dumps(value)
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
                (key, serialized, datetime.now().isoformat())
            )

    def get_cache(self, key: str) -> Optional[Dict]:
        """Retrieves and unpickles a value from the cache table."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT value, timestamp FROM cache WHERE key = ?", (key,)).fetchone()
            if row:
                return {
                    "value": pickle.loads(row[0]),
                    "timestamp": datetime.fromisoformat(row[1])
                }
        return None

    def delete_cache(self, key: str):
        """Removes a specific cache entry."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    def clear_cache(self):
        """Wipes the entire cache table."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache")

# Global DB manager instance
db_manager = DatabaseManager()
