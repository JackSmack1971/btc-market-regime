import pickle
import time
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta
from ..utils import logger

class CacheManager:
    """Disk-based caching with TTL support.
    
    This manager stores serialized objects on disk and validates their 
    freshness based on a configurable Time-To-Live (TTL).
    """
    
    def __init__(self, cache_dir: str = ".cache", default_ttl_minutes: int = 5):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
    
    def _get_cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.pkl"

    def get(self, key: str, ttl_minutes: Optional[int] = None) -> Optional[Any]:
        """Retrieves an item from cache if it exists and is not expired.
        
        Args:
            key: The unique cache identifier.
            ttl_minutes: Optional override for the default TTL.
            
        Returns:
            Optional[Any]: The cached value or None if missed/expired.
        """
        cache_file = self._get_cache_path(key)
        if not cache_file.exists():
            return None
        
        # Check TTL
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes is not None else self.default_ttl
        
        if datetime.now() - mtime > ttl:
            logger.info("Cache expired", key=key)
            try:
                cache_file.unlink()
            except OSError:
                pass
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                logger.info("Cache hit", key=key)
                return pickle.load(f)
        except (pickle.PickleError, EOFError) as e:
            logger.error("Cache read failed", key=key, error=str(e))
            return None

    def set(self, key: str, value: Any):
        """Persists a value to the disk cache.
        
        Args:
            key: The unique cache identifier.
            value: The data to persist.
        """
        cache_file = self._get_cache_path(key)
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except pickle.PickleError as e:
            logger.error("Cache write failed", key=key, error=str(e))

    def clear(self):
        """Wipes all cached files."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except OSError:
                pass
