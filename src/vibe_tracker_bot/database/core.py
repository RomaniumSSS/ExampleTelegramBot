from tortoise import Tortoise
import os
import logging
import sqlite3
import datetime


# Fix for sqlite3 not handling datetime.time by default
def adapt_time(t):
    return t.isoformat()


sqlite3.register_adapter(datetime.time, adapt_time)

# For MVP we use SQLite. In production, use os.getenv("DB_URL")
DB_URL = os.getenv("DB_URL", "sqlite://db.sqlite3")

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["src.vibe_tracker_bot.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db() -> None:
    await Tortoise.init(config=TORTOISE_ORM)

    # Enable WAL mode for SQLite to improve concurrency
    if DB_URL.startswith("sqlite://"):
        try:
            conn = Tortoise.get_connection("default")
            await conn.execute_script("PRAGMA journal_mode=WAL;")
            logging.info("Enabled SQLite WAL mode")
        except Exception as e:
            logging.warning(f"Failed to enable WAL mode: {e}")


async def close_db() -> None:
    await Tortoise.close_connections()
