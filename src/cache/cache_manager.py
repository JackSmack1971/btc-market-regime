import json
from datetime import datetime, timedelta
from typing import Any, Optional
from ..utils import logger
from ..persistence.db_manager import db_manager

class CacheManager:
    """Disk-based caching with TTL support.
    
    This manager stores serialized objects on disk and validates their 
    freshness based on a configurable Time-To-Live (TTL).
    """
    
    def __init__(self, default_ttl_minutes: int = 5):
        self.default_ttl = timedelta(minutes=default_ttl_minutes)

    def get(self, key: str, ttl_minutes: Optional[int] = None) -> Optional[Any]:
        """Retrieves and deserializes an item from cache if it exists and is not expired."""
        entry = db_manager.get_cache(key)
        if not entry:
            return None
        
        # Check TTL
        mtime = entry["timestamp"]
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes is not None else self.default_ttl
        
        if datetime.now() - mtime > ttl:
            logger.info("Cache expired (SQLite)", key=key)
            db_manager.delete_cache(key)
            return None
        
        logger.info("Cache hit (SQLite)", key=key)
        return entry["value"]

    def set(self, key: str, value: Any):
        """Persists a value to the SQLite cache."""
        try:
            db_manager.set_cache(key, value)
        except Exception as e:
            logger.error("Cache write failed (SQLite)", key=key, error=str(e))

    def clear(self):
        """Wipes all cached data in SQLite."""
        db_manager.clear_cache()
        logger.info("Cache cleared (SQLite)")
