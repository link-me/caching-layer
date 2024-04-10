from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from .cache import LRUCache
from .db import init_db, db_get, db_set, db_delete


app = FastAPI(title="Caching Layer", version="0.1.0")

# Cache: 1000 items, TTL 60s by default (configurable via env)
CAPACITY = int(os.getenv("CACHE_CAPACITY", "1000"))
TTL = int(os.getenv("CACHE_TTL_SECONDS", "60"))
cache = LRUCache(capacity=CAPACITY, ttl_seconds=TTL)


class SetRequest(BaseModel):
    key: str
    value: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "service": "caching-layer",
        "endpoints": [
            "/health",
            "/cache/get?key=...",
            "/cache/set",
            "/cache/delete?key=...",
            "/cache/stats",
        ],
        "postgres": os.getenv("DATABASE_URL", "postgresql://cache_user:cache_pass@127.0.0.1:5432/cache_db"),
        "cache": {"capacity": CAPACITY, "ttl_seconds": TTL},
    }


@app.get("/cache/stats")
def cache_stats():
    return cache.stats()


@app.get("/cache/get")
def cache_get(key: str):
    # Try cache
    val = cache.get(key)
    if val is not None:
        return {"key": key, "value": val, "source": "cache"}
    # Fallback to DB
    row = db_get(key)
    if row is None:
        raise HTTPException(status_code=404, detail="Key not found")
    cache.set(key, row["value"])
    return {"key": key, "value": row["value"], "source": "db"}


@app.post("/cache/set")
def cache_set(req: SetRequest):
    # Write-through: write to DB and cache
    db_set(req.key, req.value)
    cache.set(req.key, req.value)
    return {"ok": True}


@app.delete("/cache/delete")
def cache_delete(key: str):
    removed = cache.delete(key)
    db_removed = db_delete(key)
    return {"cache_removed": removed, "db_removed": db_removed}