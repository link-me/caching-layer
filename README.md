# Caching Layer

Сервис кеширования на Python с LRU‑кешем (TTL) и write‑through в PostgreSQL.

Стек
- Python + FastAPI — HTTP API.
- PostgreSQL — долговременное хранилище.
 - psycopg v3 (psycopg[binary]) — подключение к БД.
- Uvicorn — dev‑сервер.

Быстрый старт
1) Поднять PostgreSQL:
   - В каталоге `projects/caching-layer`: `docker compose up -d`.
   - БД: `cache_db`, пользователь: `cache_user`, пароль: `cache_pass`, порт `5432`.
2) Запустить API:
   - `./run.ps1` — создаст venv, установит зависимости и запустит на `127.0.0.1:8025`.
3) Эндпоинты:
   - `GET /health` — проверка здоровья.
   - `GET /` — информация о сервисе и конфигурации.
   - `GET /cache/get?key=foo` — получить значение; сначала из LRU, при промахе — из БД.
   - `POST /cache/set` — записать значение: `{ "key": "foo", "value": "bar" }`.
   - `DELETE /cache/delete?key=foo` — удалить из кеша и из БД.
   - `GET /cache/stats` — статистика кеша: размер, ёмкость, hits/misses, TTL.

Архитектура
- In‑memory LRU‑кеш с TTL удерживает горячие ключи.
- Write‑through: запись идёт сразу в БД и в кеш, обеспечивая консистентность.
- При чтении сначала проверяется кеш; при промахе — загрузка из БД и кеширование.

Конфигурация
- `DATABASE_URL` (опционально): по умолчанию `postgresql://cache_user:cache_pass@127.0.0.1:5432/cache_db`.
- `CACHE_CAPACITY` (опционально): по умолчанию `1000`.
- `CACHE_TTL_SECONDS` (опционально): по умолчанию `60`.

Roadmap
- См. `ROADMAP.md` (RU) и `ROADMAP.en.md` (EN) — план на 2024 по кварталам.

Примечания по зависимостям
- В проекте используется `psycopg v3` (строка `psycopg[binary]` в `requirements.txt`).
- Выбор v3 обеспечивает совместимость с Windows и Python 3.13 без необходимости `pg_config`.
- Если PostgreSQL недоступен, сервис всё равно стартует: драйвер импортируется лениво, операции с БД аккуратно деградируют.
