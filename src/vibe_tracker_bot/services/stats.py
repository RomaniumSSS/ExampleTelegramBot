from datetime import datetime, timedelta
from typing import TypedDict, Optional

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
    """
    user = await User.get_or_none(telegram_id=telegram_id)
    if not user:
        return None

    # Calculate time window (last 7 days)
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    # Fetch logs
    logs = await MoodLog.filter(user=user, created_at__gte=seven_days_ago).order_by(
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
    # Note: In a real app with multiple logs per day,
    # we might want to aggregate by day first.
    # For MVP, we just take the timestamp of the record with max/min value.
    best_log = next((log for log in logs if log.value == max_val), None)
    worst_log = next((log for log in logs if log.value == min_val), None)

    return {
        "average": round(avg_val, 1),
        "min_val": min_val,
        "max_val": max_val,
        "count": len(logs),
        "best_day_date": best_log.created_at if best_log else None,
        "worst_day_date": worst_log.created_at if worst_log else None,
    }
