from datetime import datetime
import logging
import pytz
from aiogram import Router, F, types, exceptions
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.vibe_tracker_bot.database.models import User

router = Router()
logger = logging.getLogger(__name__)

COMMON_TIMEZONES = {
    "moscow": "Europe/Moscow",
    "msk": "Europe/Moscow",
    "warsaw": "Europe/Warsaw",
    "poland": "Europe/Warsaw",
    "minsk": "Europe/Minsk",
    "kiev": "Europe/Kyiv",
    "kyiv": "Europe/Kyiv",
    "london": "Europe/London",
    "utc": "UTC",
    "gmt": "UTC",
}


class RemindersState(StatesGroup):
    waiting_for_morning_time = State()
    waiting_for_evening_time = State()
    waiting_for_timezone = State()


@router.message(Command("reminders"))
async def cmd_reminders(message: types.Message):
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        await message.answer("Пожалуйста, сначала выполните команду /start")
        return
    await show_reminders_menu(message, user)


async def show_reminders_menu(
    message: types.Message, user: User, is_edit: bool = False
):
    status_text = "✅ Включены" if user.reminders_enabled else "❌ Выключены"

    morning = "Не задано"
    if user.reminder_morning_time:
        morning = user.reminder_morning_time.strftime("%H:%M")

    evening = "Не задано"
    if user.reminder_evening_time:
        evening = user.reminder_evening_time.strftime("%H:%M")

    text = (
        f"⏰ **Настройки напоминаний**\n\n"
        f"Статус: {status_text}\n"
        f"Часовой пояс: {user.timezone}\n"
        f"Утреннее: {morning}\n"
        f"Вечернее: {evening}\n\n"
        f"Бот отправит напоминание в указанное время по вашему часовому поясу."
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Вкл/Выкл", callback_data="toggle_reminders")
    builder.button(text="Изменить утро", callback_data="set_morning")
    builder.button(text="Изменить вечер", callback_data="set_evening")
    builder.button(text="Изменить часовой пояс", callback_data="set_timezone")
    builder.adjust(1)

    try:
        if is_edit:
            await message.edit_text(
                text, reply_markup=builder.as_markup(), parse_mode="Markdown"
            )
        else:
            await message.answer(
                text, reply_markup=builder.as_markup(), parse_mode="Markdown"
            )
    except exceptions.TelegramBadRequest:
        # Ignore "Message is not modified" error
        pass


@router.callback_query(F.data == "toggle_reminders")
async def toggle_reminders(callback: types.CallbackQuery):
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    user.reminders_enabled = not user.reminders_enabled
    await user.save()
    await show_reminders_menu(callback.message, user, is_edit=True)
    await callback.answer(
        f"Напоминания {'включены' if user.reminders_enabled else 'выключены'}"
    )


@router.callback_query(F.data == "set_morning")
async def set_morning_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите время для утреннего напоминания в формате ЧЧ:ММ (например, 09:00):"
    )
    await state.set_state(RemindersState.waiting_for_morning_time)
    await callback.answer()


@router.callback_query(F.data == "set_evening")
async def set_evening_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите время для вечернего напоминания в формате ЧЧ:ММ (например, 20:00):"
    )
    await state.set_state(RemindersState.waiting_for_evening_time)
    await callback.answer()


async def validate_and_save_time(
    message: types.Message, state: FSMContext, field_name: str
):
    try:
        time_obj = datetime.strptime(message.text, "%H:%M").time()
    except ValueError:
        await message.answer(
            "Неверный формат. Пожалуйста, используйте формат ЧЧ:ММ (например, 09:30)."
        )
        return

    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        await message.answer("Пользователь не найден. Введите /start")
        return

    setattr(user, field_name, time_obj)
    await user.save()

    await state.clear()
    await message.answer("Время обновлено!")
    await show_reminders_menu(message, user)


@router.message(RemindersState.waiting_for_morning_time)
async def process_morning_time(message: types.Message, state: FSMContext):
    await validate_and_save_time(message, state, "reminder_morning_time")


@router.message(RemindersState.waiting_for_evening_time)
async def process_evening_time(message: types.Message, state: FSMContext):
    await validate_and_save_time(message, state, "reminder_evening_time")


@router.callback_query(F.data == "set_timezone")
async def set_timezone_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите название вашего города или часового пояса (на английском).\n"
        "Примеры: Warsaw, Moscow, London, Kiev\n"
        "Или полный формат: Europe/Warsaw"
    )
    await state.set_state(RemindersState.waiting_for_timezone)
    await callback.answer()


@router.message(RemindersState.waiting_for_timezone)
async def process_timezone(message: types.Message, state: FSMContext):
    tz_input = message.text.strip().lower()

    # Try common aliases first
    tz_name = COMMON_TIMEZONES.get(tz_input)

    if not tz_name:
        # Try exact match case-insensitive search in all_timezones
        for tz in pytz.all_timezones:
            if tz.lower() == tz_input:
                tz_name = tz
                break

    # If still not found, try to parse as-is
    if not tz_name:
        try:
            pytz.timezone(message.text.strip())
            tz_name = message.text.strip()
        except pytz.UnknownTimeZoneError:
            pass

    if not tz_name:
        # Try to find something ending with the input (e.g. user types "New_York")
        candidates = [tz for tz in pytz.all_timezones if tz_input in tz.lower()]
        if len(candidates) == 1:
            tz_name = candidates[0]
        elif len(candidates) > 1:
            # Ambiguous match, treat as not found to force user to be more specific
            tz_name = None

    if not tz_name:
        await message.answer(
            "Не удалось определить часовой пояс. "
            "Пожалуйста, попробуйте указать город на английском (например: Warsaw) "
            "или полный формат (Europe/Warsaw)."
        )
        return

    # Final validation
    try:
        pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        await message.answer("Ошибка валидации часового пояса. Попробуйте еще раз.")
        return

    user = await User.get_or_none(telegram_id=message.from_user.id)
    if user:
        user.timezone = tz_name
        await user.save()
        await message.answer(f"Часовой пояс установлен: {tz_name}")
        await show_reminders_menu(message, user)
    else:
        await message.answer("Пользователь не найден.")

    await state.clear()
