from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

from ..database.models import User, MoodLog
from ..services.stats import get_weekly_stats
from ..services.charts import generate_mood_chart

tracking_router = Router()


class TrackingState(StatesGroup):
    waiting_for_note = State()


async def safe_edit_text(
    message: types.Message, text: str, reply_markup: InlineKeyboardMarkup | None = None
) -> bool:
    """
    Edits message text safely, ignoring 'message is not modified' errors.
    Returns True if message was modified, False if it was already the same.
    """
    try:
        await message.edit_text(text=text, reply_markup=reply_markup)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return False
        raise


def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Creates a 1-10 rating keyboard."""
    # 2 rows of 5 buttons
    buttons = []
    row1 = [
        InlineKeyboardButton(text=str(i), callback_data=f"rate:{i}")
        for i in range(1, 6)
    ]
    row2 = [
        InlineKeyboardButton(text=str(i), callback_data=f"rate:{i}")
        for i in range(6, 11)
    ]
    buttons.append(row1)
    buttons.append(row2)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Creates a skip button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="skip_note")]
        ]
    )


def get_chart_type_keyboard() -> InlineKeyboardMarkup:
    """Creates buttons for chart period selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 За день", callback_data="chart:day"),
                InlineKeyboardButton(text="🗓 За неделю", callback_data="chart:week"),
            ]
        ]
    )


def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Creates button to view mood chart from stats."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 График настроения", callback_data="open_chart_menu"
                )
            ]
        ]
    )


@tracking_router.message(Command("log"))
async def cmd_log(message: types.Message, state: FSMContext):
    """Starts the tracking flow."""
    await state.clear()
    await message.answer(
        "Оцени свой уровень энергии/вайба от 1 до 10:",
        reply_markup=get_rating_keyboard(),
    )


@tracking_router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Shows weekly statistics."""
    stats = await get_weekly_stats(message.from_user.id)

    if not stats or stats["count"] == 0:
        await message.answer(
            "У тебя еще нет записей за последние 7 дней. Начни с /log!"
        )
        return

    # Format dates
    best_date = (
        stats["best_day_date"].strftime("%d.%m") if stats["best_day_date"] else "-"
    )
    worst_date = (
        stats["worst_day_date"].strftime("%d.%m") if stats["worst_day_date"] else "-"
    )

    text = (
        "📊 <b>Твоя статистика за 7 дней:</b>\n\n"
        f"⚡ Средний вайб: <b>{stats['average']}</b>\n"
        f"📉 Минимум: <b>{stats['min_val']}</b> ({worst_date})\n"
        f"📈 Максимум: <b>{stats['max_val']}</b> ({best_date})\n"
        f"📝 Всего записей: {stats['count']}"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_stats_keyboard())


@tracking_router.message(Command("moodchart"))
async def cmd_moodchart(message: types.Message):
    """Asks for chart period."""
    try:
        await message.answer(
            "За какой период построить график?", reply_markup=get_chart_type_keyboard()
        )
    except Exception as e:
        import logging

        logging.error(f"Error in cmd_moodchart: {e}", exc_info=True)
        await message.answer(f"Произошла ошибка при вызове команды: {e}")


@tracking_router.callback_query(F.data == "open_chart_menu")
async def process_open_chart_menu(callback: types.CallbackQuery):
    """Opens chart menu from stats button."""
    await callback.message.answer(
        "За какой период построить график?", reply_markup=get_chart_type_keyboard()
    )
    await callback.answer()


@tracking_router.callback_query(F.data.startswith("chart:"))
async def process_chart_selection(callback: types.CallbackQuery):
    """Handles chart period selection and sends the graph."""
    try:
        period = callback.data.split(":")[1]

        if not callback.message:
            return

        # Notify user that bot is working
        if not await safe_edit_text(callback.message, "Рисую график... 🎨"):
            # If message is already "Рисую график...", it means another request
            # is processing. We stop here to prevent race conditions.
            await callback.answer()
            return

        # Generate chart
        chart_buf = await generate_mood_chart(callback.from_user.id, period)

        if not chart_buf:
            await safe_edit_text(
                callback.message,
                "Недостаточно данных для графика за этот период. 😔\nПопробуй /log!",
            )
            return

        period_name = "сегодня" if period == "day" else "последние 7 дней"
        photo = BufferedInputFile(chart_buf.read(), filename=f"chart_{period}.png")

        # Delete the "Drawing..." message and send photo
        try:
            await callback.message.delete()
        except Exception:
            # Ignore if message cannot be deleted (already deleted or too old)
            pass

        await callback.message.answer_photo(
            photo=photo, caption=f"Твой график настроения за {period_name} 📊"
        )
        await callback.answer()
    except Exception as e:
        import logging

        logging.error(f"Error in process_chart_selection: {e}", exc_info=True)
        # Try to notify user, but ignore if message not modified/deleted
        try:
            await callback.message.answer(f"Ошибка при построении графика: {e}")
        except Exception:
            pass
        await callback.answer()


@tracking_router.callback_query(F.data.startswith("rate:"))
async def process_rating(callback: types.CallbackQuery, state: FSMContext):
    """Handles rating selection."""
    rating = int(callback.data.split(":")[1])
    await state.update_data(rating=rating)
    await state.set_state(TrackingState.waiting_for_note)

    await safe_edit_text(
        callback.message,
        f"Принято: {rating}/10.\n\n"
        "Хочешь добавить заметку? Напиши её или нажми кнопку:",
        reply_markup=get_skip_keyboard(),
    )
    await callback.answer()


@tracking_router.message(TrackingState.waiting_for_note)
async def process_note(message: types.Message, state: FSMContext):
    """Handles the text note."""
    data = await state.get_data()
    rating = data.get("rating")
    note = message.text

    user, _ = await User.get_or_create(
        telegram_id=message.from_user.id,
        defaults={"username": message.from_user.username},
    )

    await MoodLog.create(user=user, value=rating, note=note)

    await state.clear()
    await message.answer("✅ Запись сохранена!")


@tracking_router.callback_query(F.data == "skip_note", TrackingState.waiting_for_note)
async def process_skip_note(callback: types.CallbackQuery, state: FSMContext):
    """Handles skipping the note."""
    data = await state.get_data()
    rating = data.get("rating")

    user, _ = await User.get_or_create(
        telegram_id=callback.from_user.id,
        defaults={"username": callback.from_user.username},
    )

    await MoodLog.create(user=user, value=rating, note=None)

    await state.clear()
    await safe_edit_text(
        callback.message, f"Принято: {rating}/10.\n✅ Запись сохранена (без заметки)."
    )
    await callback.answer()
