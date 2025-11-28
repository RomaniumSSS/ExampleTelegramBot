import time
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        start_time = time.time()

        # Process the event
        result = await handler(event, data)

        # Calculate duration
        duration = time.time() - start_time

        # Get event info
        event_name = event.__class__.__name__
        user_id = "unknown"

        # Try to extract user_id safely
        # "from_user" exists on Message, CallbackQuery, InlineQuery, etc.
        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id
        elif (
            hasattr(event, "message")
            and hasattr(event.message, "from_user")
            and event.message.from_user
        ):
            # Fallback for events that might not have from_user directly
            pass

        # Log if slow (> 1s)
        if duration > 1.0:
            logger.warning(
                f"SLOW HANDLER: {event_name} from {user_id} took {duration:.2f}s"
            )
        else:
            logger.info(f"Handled {event_name} from {user_id} in {duration:.2f}s")

        return result
