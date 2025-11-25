from __future__ import annotations

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .tracking import get_rating_keyboard


onboarding_router = Router()


class OnboardingState(StatesGroup):
    in_progress = State()


class OnboardingQuestion:
    def __init__(self, title: str, options: list[str], hint: str | None = None):
        self.title = title
        self.options = options
        self.hint = hint


QUESTIONS: list[OnboardingQuestion] = [
    OnboardingQuestion(
        title="Как часто чувствуете упадок энергии?",
        options=[
            "Редко (1–2 раза в месяц)",
            "Пару раз в неделю",
            "Практически ежедневно",
        ],
    ),
    OnboardingQuestion(
        title="Что сильнее влияет на ваше состояние?",
        options=["Работа", "Учёба", "Семья / отношения", "Неопределённо"],
    ),
    OnboardingQuestion(
        title="Что хотите отслеживать в первую очередь?",
        options=["Энергия", "Настроение", "Оба сразу"],
        hint="Можно менять в любой момент",
    ),
    OnboardingQuestion(
        title="Как удобнее получать помощь?",
        options=["2 напоминания в день", "Вечерний дайджест", "Без напоминаний"],
    ),
    OnboardingQuestion(
        title="Готовы начать с первого лога?",
        options=["Да, сейчас", "Напомнить через день", "Посмотреть сначала"],
        hint="80% людей находят триггеры за 7 дней",
    ),
]


def _build_question_text(index: int) -> str:
    question = QUESTIONS[index]
    progress = f"Вопрос {index + 1}/{len(QUESTIONS)}"
    parts = [f"{progress}\n\n{question.title}"]
    if question.hint:
        parts.append(f"\n💡 {question.hint}")
    return "".join(parts)


def _question_keyboard(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=option,
                    callback_data=f"onboard:q:{index}:{idx}",
                )
            ]
            for idx, option in enumerate(QUESTIONS[index].options)
        ],
    )


def _cta_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Сделать первый лог", callback_data="onboard:log")],
            [InlineKeyboardButton(text="Позже", callback_data="onboard:finish")],
        ]
    )


@onboarding_router.callback_query(F.data == "onboard:start")
async def start_onboarding(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(OnboardingState.in_progress)
    await state.update_data(answers={})

    await callback.message.edit_text(
        "Соберу твой персональный трекер за 5 вопросов."
        " Можно остановиться в любой момент.",
    )

    await callback.message.answer(
        _build_question_text(0), reply_markup=_question_keyboard(0)
    )
    await callback.answer()


@onboarding_router.callback_query(F.data == "onboard:skip")
async def skip_onboarding(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Ок, можно сразу перейти к основным командам:\n"
        "📝 /log — отметить своё состояние\n"
        "📊 /stats — статистика за неделю",
    )
    await callback.answer()


@onboarding_router.callback_query(
    F.data.startswith("onboard:q:"), OnboardingState.in_progress
)
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    _, _, q_index_str, option_idx_str = callback.data.split(":")
    question_index = int(q_index_str)
    option_index = int(option_idx_str)

    data = await state.get_data()
    answers = data.get("answers", {})
    answers[question_index] = QUESTIONS[question_index].options[option_index]
    await state.update_data(answers=answers)

    next_index = question_index + 1

    if next_index >= len(QUESTIONS):
        await state.clear()
        await _finish_flow(callback, answers)
        return

    await callback.message.edit_text(
        _build_question_text(next_index), reply_markup=_question_keyboard(next_index)
    )
    await callback.answer()


async def _finish_flow(callback: types.CallbackQuery, answers: dict[int, str]):
    primary_goal = answers.get(2, "энергия и настроение")
    reminder_pref = answers.get(3, "без напоминаний")

    summary = (
        "Готово! Я настроил флоу под тебя.\n\n"
        f"🔍 Фокус: {primary_goal}\n"
        f"⏰ Напоминания: {reminder_pref}\n\n"
        "Первые 7 дней покажу лучшие и худшие часы."
    )

    await callback.message.edit_text(summary, reply_markup=_cta_keyboard())
    await callback.answer()


@onboarding_router.callback_query(F.data == "onboard:log")
async def go_to_log(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Оцени свой уровень энергии/вайба от 1 до 10:",
        reply_markup=get_rating_keyboard(),
    )
    await callback.answer()


@onboarding_router.callback_query(F.data == "onboard:finish")
async def finish_without_log(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Без проблем! Когда будешь готов — набери /log, чтобы сделать первую запись."
    )
    await callback.answer()
