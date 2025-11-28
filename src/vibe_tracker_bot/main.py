import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from src.vibe_tracker_bot.database.core import init_db, close_db
from src.vibe_tracker_bot.handlers import common, tracking

# Load environment variables
load_dotenv()


async def set_commands(bot: Bot):
    """Sets the bot's command list."""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="log", description="Отметить вайб"),
        BotCommand(command="stats", description="Статистика"),
        BotCommand(command="moodchart", description="График настроения"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(dispatcher: Dispatcher):
    logging.info("Starting up...")
    await init_db()


async def on_shutdown(dispatcher: Dispatcher):
    logging.info("Shutting down...")
    await close_db()


async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logging.error("BOT_TOKEN is not set in environment variables")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Register routers
    dp.include_router(common.router)
    dp.include_router(tracking.tracking_router)

    # Register startup/shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logging.info("Bot started")
    try:
        # Set commands on startup
        await set_commands(bot)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
