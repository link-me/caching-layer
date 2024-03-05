from collections import OrderedDict
import time
from typing import Any, Optional


class LRUCache:
    def __init__(self, capacity: int = 1024, ttl_seconds: Optional[int] = None):
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.store: "OrderedDict[str, tuple[Any, Optional[float]]]" = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _expired(self, expires_at: Optional[float]) -> bool:
        return expires_at is not None and time.time() > expires_at

    def get(self, key: str) -> Optional[Any]:
        item = self.store.get(key)
        if item is None:
            self.misses += 1
            return None
        value, expires_at = item
        if self._expired(expires_at):
            # Remove expired
            self.store.pop(key, None)
            self.misses += 1
            return None
        # Move to end (most recent)
        self.store.move_to_end(key)
        self.hits += 1
        return value

    def set(self, key: str, value: Any) -> None:
        expires_at = None
        if self.ttl:
            expires_at = time.time() + self.ttl
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = (value, expires_at)
        # Evict LRU if over capacity
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)

    def delete(self, key: str) -> bool:
        return self.store.pop(key, None) is not None

    def stats(self) -> dict:
        return {
            "size": len(self.store),
            "capacity": self.capacity,
            "hits": self.hits,
            "misses": self.misses,
            "ttl_seconds": self.ttl,
        }