import asyncio
import io
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pytz
from ..database.models import MoodLog, User


def _draw_chart(dates: list, values: list, title: str, period: str) -> io.BytesIO:
    """
    Synchronous function to draw chart using matplotlib (OO interface).
    Run this in a separate thread to avoid blocking the event loop.
    """
    # Create figure and axes directly (Stateless approach)
    fig = Figure(figsize=(10, 6), dpi=100)
    FigureCanvasAgg(fig)  # Attach canvas
    ax = fig.add_subplot(111)

    # Plot data
    ax.plot(
        dates,
        values,
        marker="o",
        linestyle="-",
        color="#4CAF50",
        linewidth=2,
        markersize=8,
    )

    # Customize axes
    ax.set_title(title, fontsize=14, pad=10)
    ax.set_ylabel("Vibe Level", fontsize=12)
    ax.set_ylim(0, 11)  # 0 to 11 to show 1 and 10 clearly
    ax.set_yticks(range(1, 11))
    ax.grid(True, linestyle="--", alpha=0.7)

    # Format Date Axis
    if period == "day":
        date_fmt = mdates.DateFormatter("%H:%M")
        ax.xaxis.set_major_formatter(date_fmt)
        # Ensure we see some hours if few points
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    else:
        date_fmt = mdates.DateFormatter("%d.%m")
        ax.xaxis.set_major_formatter(date_fmt)
        ax.xaxis.set_major_locator(mdates.DayLocator())

    fig.autofmt_xdate()

    # Save to buffer using FigureCanvasAgg
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    # No need to plt.close(fig) as we didn't use the global state
    return buf


async def generate_mood_chart(user_id: int, period: str) -> io.BytesIO | None:
    """
    Generates a mood chart for the specified period ('day' or 'week').
    Returns a BytesIO object containing the image, or None if no data.
    """
    user = await User.get_or_none(telegram_id=user_id)
    if not user:
        return None

    # Resolve User Timezone
    try:
        user_tz = pytz.timezone(user.timezone)
    except (pytz.UnknownTimeZoneError, AttributeError):
        user_tz = pytz.utc

    # Current UTC time
    now_utc = datetime.now(pytz.utc)
    # Current User time
    now_user = now_utc.astimezone(user_tz)

    if period == "day":
        # Start of today in USER's timezone
        start_of_day_user = now_user.replace(hour=0, minute=0, second=0, microsecond=0)
        # Convert back to UTC for DB filtering
        # Note: We assume DB stores Naive UTC or Aware UTC.
        # Tortoise usually stores naive UTC if not configured otherwise.
        start_time_utc = start_of_day_user.astimezone(pytz.utc)

        title = "Mood Chart (Today)"
    elif period == "week":
        # Last 7 days relative to now
        start_time_utc = now_utc - timedelta(days=7)
        title = "Mood Chart (Last 7 Days)"
    else:
        return None

    # Filter logs. Tortoise might expect naive datetime if fields are naive.
    # Using naive UTC for safety with SQLite default
    start_time_naive = start_time_utc.replace(tzinfo=None)

    logs = await MoodLog.filter(user=user, created_at__gte=start_time_naive).order_by(
        "created_at"
    )

    if not logs:
        return None

    # Prepare data for plotting
    dates = []
    values = []

    for log in logs:
        # log.created_at is likely naive UTC from DB
        created_at = log.created_at
        if created_at.tzinfo is None:
            created_at = pytz.utc.localize(created_at)

        # Convert to user timezone for display
        local_time = created_at.astimezone(user_tz)
        dates.append(local_time)
        values.append(log.value)

    # Run blocking plotting code in a separate thread
    return await asyncio.to_thread(_draw_chart, dates, values, title, period)
