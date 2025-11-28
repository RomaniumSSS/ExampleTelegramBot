import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from src.vibe_tracker_bot.database.core import init_db, close_db
from src.vibe_tracker_bot.handlers import common, tracking, reminders
from src.vibe_tracker_bot.middlewares.event_logging import LoggingMiddleware
from src.vibe_tracker_bot.services.scheduler import start_scheduler

# Load environment variables
load_dotenv()


async def set_commands(bot: Bot):
    """Sets the bot's command list."""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="log", description="Отметить вайб"),
        BotCommand(command="stats", description="Статистика"),
        BotCommand(command="moodchart", description="График настроения"),
        BotCommand(command="reminders", description="Напоминания"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    logging.info("Starting up...")
    await init_db()
    # Start scheduler after DB is ready
    start_scheduler(bot)


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

    # Register middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Register routers
    dp.include_router(common.router)
    dp.include_router(tracking.tracking_router)
    dp.include_router(reminders.router)

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
