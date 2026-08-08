import hashlib
import threading
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    frequency: int = 1


class LFUCache:
    def __init__(self, max_size):

        self.max_size = max_size

        self._cache: dict[str, CacheEntry] = {}
        # Agar ek saath multiple requests aa rahi hain to lock ensure karta hai ki _cache ko safely access/modify kiya jaaye.
        self._lock = threading.Lock()

    @staticmethod
    def _make_key(key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(self, key: str):
        hashed_key = self._make_key(key)
        with self._lock:
            entry = self._cache.get(hashed_key)
            if entry is None:
                return None

            # Increase frequency
            entry.frequency += 1
            return entry.value

    def set(self,key: str,value: Any):
        hashed_key = self._make_key(key)
        with self._lock:
            # Already exists
            if hashed_key in self._cache:
                entry = self._cache[hashed_key]
                entry.value = value
                entry.frequency += 1
                return
            
            # Cache full
            if len(self._cache) >= self.max_size:
                self._evict_lfu()

            # Add new item
            self._cache[hashed_key] = CacheEntry( value=value,frequency=1)

    def _evict_lfu(self):
        if not self._cache:
            return
        least_used_key = min(self._cache,key=lambda key:self._cache[key].frequency)

        del self._cache[least_used_key]


    def delete(self, key: str):
        hashed_key = self._make_key(key)
        with self._lock:
            self._cache.pop(hashed_key,None)


    def clear(self):
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def stats(self):

        with self._lock:
            entries = []
            for key, entry in self._cache.items():
                entries.append({"key": key,
                    "frequency": entry.frequency})

            entries.sort(key=lambda x: x["frequency"],reverse=True)

            return {"size": len(self._cache),
                "max_size": self.max_size,
                "entries": entries}

cache = LFUCache(
    max_size=100
)
