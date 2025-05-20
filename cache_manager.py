"""Cache manager for the application."""
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._access_count: Dict[str, int] = {}
        self._last_access: Dict[str, datetime] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key not in self._cache:
            return None
        
        # Check if entry has expired
        if self._is_expired(key):
            self.delete(key)
            return None
            
        # Update access statistics
        self._access_count[key] += 1
        self._last_access[key] = datetime.now()
        
        return self._cache[key]["value"]

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set a value in cache."""
        # Clean up if cache is full
        if len(self._cache) >= self._max_size:
            self._cleanup()
            
        expiry = datetime.now() + timedelta(seconds=ttl_seconds or self._ttl_seconds)
        
        self._cache[key] = {
            "value": value,
            "expiry": expiry
        }
        self._access_count[key] = 0
        self._last_access[key] = datetime.now()

    def delete(self, key: str) -> None:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]
            del self._access_count[key]
            del self._last_access[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_count.clear()
        self._last_access.clear()

    def get_keys(self) -> Set[str]:
        """Get all valid cache keys."""
        return {k for k in self._cache.keys() if not self._is_expired(k)}

    def _is_expired(self, key: str) -> bool:
        """Check if a cache entry has expired."""
        if key not in self._cache:
            return True
        return datetime.now() > self._cache[key]["expiry"]

    def _cleanup(self) -> None:
        """Clean up expired and least recently used entries."""
        # Remove expired entries
        expired_keys = [k for k in self._cache.keys() if self._is_expired(k)]
        for key in expired_keys:
            self.delete(key)
            
        # If still over max size, remove least recently used entries
        if len(self._cache) >= self._max_size:
            sorted_keys = sorted(
                self._last_access.items(),
                key=lambda x: (self._access_count[x[0]], x[1])
            )
            for key, _ in sorted_keys[:len(self._cache) - self._max_size + 1]:
                self.delete(key)

class DataCache:
    def __init__(self):
        # Separate caches for different types of data
        self.student_cache = CacheManager(max_size=1000, ttl_seconds=3600)
        self.subject_cache = CacheManager(max_size=500, ttl_seconds=3600)
        self.grade_cache = CacheManager(max_size=2000, ttl_seconds=1800)
        self.stat_cache = CacheManager(max_size=200, ttl_seconds=900)

    def invalidate_student(self, ma_sv: Optional[str] = None) -> None:
        """Invalidate student cache."""
        if ma_sv:
            self.student_cache.delete(ma_sv)
            # Also invalidate related grade cache
            grade_keys = [k for k in self.grade_cache.get_keys() if ma_sv in k]
            for key in grade_keys:
                self.grade_cache.delete(key)
        else:
            self.student_cache.clear()
            self.grade_cache.clear()

    def invalidate_subject(self, ma_mh: Optional[str] = None) -> None:
        """Invalidate subject cache."""
        if ma_mh:
            self.subject_cache.delete(ma_mh)
            # Also invalidate related grade cache
            grade_keys = [k for k in self.grade_cache.get_keys() if ma_mh in k]
            for key in grade_keys:
                self.grade_cache.delete(key)
        else:
            self.subject_cache.clear()
            self.grade_cache.clear()

    def invalidate_grade(self, ma_sv: Optional[str] = None,
                        ma_mh: Optional[str] = None,
                        hoc_ky: Optional[str] = None) -> None:
        """Invalidate grade cache."""
        if any([ma_sv, ma_mh, hoc_ky]):
            grade_keys = self.grade_cache.get_keys()
            for key in grade_keys:
                should_delete = False
                if ma_sv and ma_sv in key:
                    should_delete = True
                if ma_mh and ma_mh in key:
                    should_delete = True
                if hoc_ky and hoc_ky in key:
                    should_delete = True
                if should_delete:
                    self.grade_cache.delete(key)
        else:
            self.grade_cache.clear()
        
        # Always invalidate statistics when grades change
        self.stat_cache.clear()

    def invalidate_all(self) -> None:
        """Invalidate all caches."""
        self.student_cache.clear()
        self.subject_cache.clear()
        self.grade_cache.clear()
        self.stat_cache.clear()
