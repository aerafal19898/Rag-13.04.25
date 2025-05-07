import redis
import json
import logging
import os
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages interactions with a Redis cache server."""

    def __init__(self, host: str = None, port: int = None, db: int = 0):
        """Initialize the Redis connection.

        Args:
            host: Redis server host (defaults to env var REDIS_HOST or 'localhost').
            port: Redis server port (defaults to env var REDIS_PORT or 6379).
            db: Redis database number (defaults to 0).
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", 6379))
        self.db = db
        # Use REDIS_PASSWORD environment variable for production secret
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.client = None
        self._connect()

    def _connect(self):
        """Establish connection to Redis server."""
        try:
            # Use decode_responses=True to get strings directly
            # Use REDIS_PASSWORD if set
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            self.client.ping() # Check connection
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis at {self.host}:{self.port}: {e}")
            self.client = None # Ensure client is None if connection fails

    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self.client is not None

    def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """Set a key-value pair in the cache, optionally with an expiry.

        Args:
            key: The cache key.
            value: The value to store (will be JSON serialized if not string/bytes).
            expire_seconds: Optional expiry time in seconds.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_connected():
            logger.warning("Cannot set cache: Redis not connected.")
            return False
        try:
            # Serialize complex types to JSON
            if not isinstance(value, (str, bytes, int, float)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)

            if expire_seconds:
                return self.client.setex(key, expire_seconds, value_str)
            else:
                return self.client.set(key, value_str)
        except redis.exceptions.RedisError as e:
            logger.error(f"Error setting cache key '{key}': {e}")
            return False
        except TypeError as e:
            logger.error(f"Error serializing value for key '{key}': {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache by key.

        Args:
            key: The cache key.

        Returns:
            The cached value (deserialized if JSON), or None if not found or error.
        """
        if not self.is_connected():
            logger.warning("Cannot get cache: Redis not connected.")
            return None
        try:
            value_str = self.client.get(key)
            if value_str is None:
                return None
            # Attempt to deserialize if it looks like JSON
            try:
                if value_str.startswith(('{', '[')):
                     return json.loads(value_str)
            except json.JSONDecodeError:
                pass # Return as string if not valid JSON
            return value_str # Return as string if not JSON or simple type
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting cache key '{key}': {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key from the cache.

        Args:
            key: The cache key to delete.

        Returns:
            True if successful (or key didn't exist), False on error.
        """
        if not self.is_connected():
            logger.warning("Cannot delete cache: Redis not connected.")
            return False
        try:
            self.client.delete(key)
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Error deleting cache key '{key}': {e}")
            return False

    def close(self):
        """Close the Redis connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("Redis connection closed.")
            except redis.exceptions.RedisError as e:
                logger.error(f"Error closing Redis connection: {e}")
            self.client = None 