from .cache_manager import CacheManager

# Global cache instance for the application
cache = CacheManager()

__all__ = ["CacheManager", "cache"]
