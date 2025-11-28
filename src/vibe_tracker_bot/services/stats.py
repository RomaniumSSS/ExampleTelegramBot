from datetime import datetime, timedelta
from typing import TypedDict, Optional
import pytz

from ..database.models import MoodLog, User


class StatsResult(TypedDict):
    average: float
    min_val: int
    max_val: int
    count: int
    best_day_date: Optional[datetime]
    worst_day_date: Optional[datetime]


async def get_weekly_stats(telegram_id: int) -> Optional[StatsResult]:
    """
    Calculates statistics for the last 7 days for a given user.
    Respects user's timezone for the day boundary.
    """
    user = await User.get_or_none(telegram_id=telegram_id)
    if not user:
        return None

    # Resolve User Timezone
    try:
        user_tz = pytz.timezone(user.timezone)
    except (pytz.UnknownTimeZoneError, AttributeError):
        user_tz = pytz.utc

    # Calculate time window (last 7 days) relative to user's "now"
    now_utc = datetime.now(pytz.utc)
    now_user = now_utc.astimezone(user_tz)

    # Start of 7 days ago in user time
    seven_days_ago_user = now_user - timedelta(days=7)

    # Convert back to UTC for DB query (assuming DB stores naive UTC or we strip info)
    start_time_utc = seven_days_ago_user.astimezone(pytz.utc)

    # Tortoise/SQLite usually work with naive UTC.
    start_time_naive = start_time_utc.replace(tzinfo=None)

    # Fetch logs
    logs = await MoodLog.filter(user=user, created_at__gte=start_time_naive).order_by(
        "-created_at"
    )

    if not logs:
        return {
            "average": 0.0,
            "min_val": 0,
            "max_val": 0,
            "count": 0,
            "best_day_date": None,
            "worst_day_date": None,
        }

    values = [log.value for log in logs]

    # Calculate metrics
    avg_val = sum(values) / len(values)
    min_val = min(values)
    max_val = max(values)

    # Find specific logs for dates
    best_log = next((log for log in logs if log.value == max_val), None)
    worst_log = next((log for log in logs if log.value == min_val), None)

    # Helper to convert log time to user timezone
    def to_user_tz(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        return dt.astimezone(user_tz)

    return {
        "average": round(avg_val, 1),
        "min_val": min_val,
        "max_val": max_val,
        "count": len(logs),
        "best_day_date": to_user_tz(best_log.created_at) if best_log else None,
        "worst_day_date": to_user_tz(worst_log.created_at) if worst_log else None,
    }
