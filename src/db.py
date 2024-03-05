import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_conn():
    dsn = os.getenv(
        "DATABASE_URL",
        "postgresql://cache_user:cache_pass@127.0.0.1:5432/cache_db",
    )
    return psycopg2.connect(dsn)


def init_db():
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    );
                    """
                )
    finally:
        conn.close()


def db_get(key: str) -> dict | None:
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT key, value, updated_at FROM cache_entries WHERE key=%s", (key,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def db_set(key: str, value: str) -> None:
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cache_entries (key, value)
                    VALUES (%s, %s)
                    ON CONFLICT (key)
                    DO UPDATE SET value=EXCLUDED.value, updated_at=NOW();
                    """,
                    (key, value),
                )
    finally:
        conn.close()


def db_delete(key: str) -> bool:
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cache_entries WHERE key=%s", (key,))
                return cur.rowcount > 0
    finally:
        conn.close()