import redis
import json
import logging
import os
from typing import Optional, Any

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))
        self.password = os.getenv("REDIS_PASSWORD", None)
        
        self.client = None
        self._local_cache = {} # Fallback memory cache
        
        try:
            self.client = redis.Redis(
                host=self.host, 
                port=self.port, 
                db=self.db, 
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis connected at {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to in-memory cache.")
            self.client = None

    def set(self, key: str, value: Any, expire: int = 43200):
        """Default expire 12 hours (43200 seconds)"""
        serialized = json.dumps(value, ensure_ascii=False)
        if self.client:
            try:
                self.client.set(key, serialized, ex=expire)
                return
            except Exception as e:
                logger.error(f"Redis set failed: {e}")
        
        # Fallback
        self._local_cache[key] = {
            "data": value,
            "expire_at": 0 # Simplistic fallback
        }

    def get(self, key: str) -> Optional[Any]:
        if self.client:
            try:
                data = self.client.get(key)
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                logger.error(f"Redis get failed: {e}")

        # Fallback
        entry = self._local_cache.get(key)
        if entry:
            return entry["data"]
        return None

    def delete(self, key: str):
        if self.client:
            try:
                self.client.delete(key)
            except: pass
        
        if key in self._local_cache:
            del self._local_cache[key]

cache_service = CacheService()
