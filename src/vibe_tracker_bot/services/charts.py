import asyncio
import io
import matplotlib

# Set backend before importing pyplot to avoid GUI issues
try:
    matplotlib.use("Agg")
except Exception:
    pass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from ..database.models import MoodLog, User


def _draw_chart(dates: list, values: list, title: str, period: str) -> io.BytesIO:
    """
    Synchronous function to draw chart using matplotlib.
    Run this in a separate thread to avoid blocking the event loop.
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

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

    # Save to buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    buf.seek(0)

    # Close figure to free memory
    plt.close(fig)

    return buf


async def generate_mood_chart(user_id: int, period: str) -> io.BytesIO | None:
    """
    Generates a mood chart for the specified period ('day' or 'week').
    Returns a BytesIO object containing the image, or None if no data.
    """
    user = await User.get_or_none(telegram_id=user_id)
    if not user:
        return None

    now = datetime.now()

    if period == "day":
        # Start of today (00:00)
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        title = "Mood Chart (Today)"
    elif period == "week":
        # Last 7 days
        start_time = now - timedelta(days=7)
        title = "Mood Chart (Last 7 Days)"
    else:
        return None

    logs = await MoodLog.filter(user=user, created_at__gte=start_time).order_by(
        "created_at"
    )

    if not logs:
        return None

    dates = [log.created_at for log in logs]
    values = [log.value for log in logs]

    # Run blocking plotting code in a separate thread
    return await asyncio.to_thread(_draw_chart, dates, values, title, period)
