"""Caching layer for Census API responses."""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from diskcache import Cache
from pydantic import BaseModel


class CacheEntry(BaseModel):
    """A cached response with metadata."""

    data: Any
    cached_at: datetime
    expires_at: datetime
    cache_key: str
    hit_count: int = 0


class CensusCache:
    """Disk-based cache for Census API responses.

    Census data changes infrequently (annually for most datasets),
    so aggressive caching improves performance significantly.
    """

    # Default cache durations by data type
    CACHE_DURATIONS = {
        "datasets": timedelta(days=7),  # Dataset metadata
        "geography": timedelta(days=30),  # Geography mappings
        "fips": timedelta(days=90),  # FIPS codes rarely change
        "aggregate": timedelta(days=1),  # Actual data (conservative)
    }

    def __init__(self, cache_dir: str | Path = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = Cache(str(self.cache_dir))

    def _generate_key(self, operation: str, params: dict[str, Any]) -> str:
        """Generate a unique cache key from operation and parameters."""
        param_str = json.dumps(params, sort_keys=True)
        hash_input = f"{operation}:{param_str}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def get(self, operation: str, params: dict[str, Any]) -> Any | None:
        """Retrieve cached data if available and not expired."""
        key = self._generate_key(operation, params)

        if key in self._cache:
            entry_data = self._cache[key]
            entry = CacheEntry.model_validate(entry_data)

            if datetime.utcnow() < entry.expires_at:
                # Update hit count
                entry.hit_count += 1
                self._cache[key] = entry.model_dump(mode="json")
                return entry.data

            # Expired - remove from cache
            del self._cache[key]

        return None

    def set(
        self,
        operation: str,
        params: dict[str, Any],
        data: Any,
        duration: timedelta | None = None,
    ) -> str:
        """Cache data with automatic expiration."""
        key = self._generate_key(operation, params)

        # Determine cache duration
        if duration is None:
            duration = self.CACHE_DURATIONS.get(operation, timedelta(hours=1))

        now = datetime.utcnow()
        entry = CacheEntry(
            data=data,
            cached_at=now,
            expires_at=now + duration,
            cache_key=key,
        )

        self._cache[key] = entry.model_dump(mode="json")
        return key

    def invalidate(self, operation: str, params: dict[str, Any]) -> bool:
        """Invalidate a specific cache entry."""
        key = self._generate_key(operation, params)
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear_all(self) -> int:
        """Clear all cached data. Returns count of cleared entries."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        total_size = self._cache.volume()

        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "cache_directory": str(self.cache_dir),
        }

    def close(self):
        """Close the cache connection."""
        self._cache.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
