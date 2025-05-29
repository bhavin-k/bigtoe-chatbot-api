import time
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheEntry:
    def __init__(self, data, timestamp=None, ttl=3600):
        self.data = data
        self.timestamp = timestamp or time.time()
        self.ttl = ttl
    
    def is_expired(self):
        return time.time() > (self.timestamp + self.ttl)

class CacheManager:
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
    
    def get(self, cache_key: str, ttl: int = 3600) -> Optional[Any]:
        """Get data from cache if it exists and is not expired"""
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if not cache_entry.is_expired():
                logger.info(f"Cache hit for key: {cache_key}")
                return cache_entry.data
            else:
                logger.info(f"Cache expired for key: {cache_key}")
                del self.cache[cache_key]
        else:
            logger.info(f"Cache miss for key: {cache_key}")
        return None

    def set(self, cache_key: str, data: Any, ttl: int = 3600):
        """Store data in cache with given TTL"""
        self.cache[cache_key] = CacheEntry(data, ttl=ttl)
        logger.info(f"Stored in cache: {cache_key}")

# Global cache instance
cache_manager = CacheManager()