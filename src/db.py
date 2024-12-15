import os

def get_conn():
    try:
        import psycopg
        from psycopg.rows import dict_row
    except Exception:
        return None
    try:
        dsn = os.getenv(
            "DATABASE_URL",
            "postgresql://cache_user:cache_pass@127.0.0.1:5432/cache_db",
        )
        conn = psycopg.connect(dsn, row_factory=dict_row, connect_timeout=3)
        return conn
    except Exception:
        return None


def init_db() -> bool:
    conn = get_conn()
    if not conn:
        return False
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
        return True
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def db_get(key: str) -> dict | None:
    conn = get_conn()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT key, value, updated_at FROM cache_entries WHERE key=%s", (key,))
            row = cur.fetchone()
            return row if row else None
    except Exception:
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def db_set(key: str, value: str) -> bool:
    conn = get_conn()
    if not conn:
        return False
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
        return True
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def db_delete(key: str) -> bool:
    conn = get_conn()
    if not conn:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cache_entries WHERE key=%s", (key,))
                return cur.rowcount > 0
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass