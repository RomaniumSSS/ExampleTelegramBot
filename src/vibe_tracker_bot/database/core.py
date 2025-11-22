from tortoise import Tortoise
import os

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
    pass


async def close_db() -> None:
    await Tortoise.close_connections()
