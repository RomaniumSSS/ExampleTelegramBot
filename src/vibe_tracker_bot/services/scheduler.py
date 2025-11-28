import datetime
import logging
import pytz
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.vibe_tracker_bot.database.models import User

logger = logging.getLogger(__name__)


async def send_reminders(bot: Bot):
    # Get current UTC time
    utc_now = datetime.datetime.now(pytz.utc)

    # Fetch all users with reminders enabled
    # In MVP with few users, fetching all is fine.
    # For scale, we would need to batch or optimize queries.
    try:
        users = await User.filter(reminders_enabled=True).all()
    except Exception as e:
        logger.error(f"Error querying users for reminders: {e}")
        return

    logger.debug(f"Scheduler run at {utc_now}. Checking {len(users)} users.")

    users_to_notify = []

    for user in users:
        try:
            # Get user's timezone (default to UTC if invalid)
            try:
                tz = pytz.timezone(user.timezone)
            except pytz.UnknownTimeZoneError:
                tz = pytz.utc

            # Convert UTC now to user's local time
            user_now = utc_now.astimezone(tz)

            # Check morning reminder
            if user.reminder_morning_time:
                # We check if current time matches the reminder time (ignoring seconds)
                if (
                    user_now.hour == user.reminder_morning_time.hour
                    and user_now.minute == user.reminder_morning_time.minute
                ):
                    users_to_notify.append(user.telegram_id)
                    continue  # Don't send double reminder if times overlap (unlikely)

            # Check evening reminder
            if user.reminder_evening_time:
                if (
                    user_now.hour == user.reminder_evening_time.hour
                    and user_now.minute == user.reminder_evening_time.minute
                ):
                    users_to_notify.append(user.telegram_id)
        except Exception as e:
            logger.error(f"Error processing user {user.telegram_id}: {e}")
            continue

    if not users_to_notify:
        return

    logger.info(f"Sending reminders to {len(users_to_notify)} users.")

    for telegram_id in users_to_notify:
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text="👋 Привет! Как твое настроение? Давай затрекаем вайб! /log",
            )
        except Exception as e:
            logger.error(f"Failed to send reminder to user {telegram_id}: {e}")


def start_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    # Check every minute
    scheduler.add_job(send_reminders, "interval", minutes=1, args=[bot])
    scheduler.start()
    logger.info("Scheduler started")
