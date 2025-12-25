from aiogram import Router, F
from aiogram.types import Message
from datetime import date

from bot.config import PASSWORD
from bot.keyboards import main_keyboard
from bot.storage import balances, daily_stats, monthly_stats, update_balance
from bot.charts import build_daily_chart

router = Router()

authorized_users = set()
waiting_for_amount = {}
operation_type = {}


@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Использование бота возможно после ввода уникального пароля.\n"
        "Пожалуйста, вводите пароль:"
    )


@router.message(F.text == PASSWORD)
async def correct_password(message: Message):
    authorized_users.add(message.from_user.id)
    await message.answer(
        "Доступ разрешен. Доходы и расходы вводить с помощью команд!",
        reply_markup=main_keyboard
    )


@router.message(lambda m: m.from_user.id not in authorized_users)
async def denied(message: Message):
    await message.answer("Доступ ограничен!")


@router.message(F.text.in_(["доход", "расход"]))
async def choose_operation(message: Message):
    waiting_for_amount[message.from_user.id] = True
    operation_type[message.from_user.id] = message.text
    await message.answer("Введите сумму:")


@router.message()
async def process_amount(message: Message):
    user_id = message.from_user.id

    if not waiting_for_amount.get(user_id):
        return

    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    if operation_type[user_id] == "расход":
        amount = -amount

    update_balance(user_id, amount)

    balance = balances[user_id]
    sign = "+" if balance >= 0 else ""

    await message.answer(
        f"{sign}{balance:.2f} BYN",
        reply_markup=main_keyboard
    )

    waiting_for_amount[user_id] = False


@router.message(F.text == "день")
async def day_balance(message: Message):
    today = date.today().isoformat()
    amount = daily_stats[message.from_user.id].get(today, 0.0)
    await message.answer(f"Дневной баланс: {amount:.2f} BYN")


@router.message(F.text == "месяц")
async def month_balance(message: Message):
    month = date.today().isoformat()[:7]
    amount = monthly_stats[message.from_user.id].get(month, 0.0)
    await message.answer(f"Месячный баланс: {amount:.2f} BYN")


@router.message(F.text == "график")
async def graph(message: Message):
    chart = build_daily_chart(daily_stats, message.from_user.id)
    if chart:
        await message.answer_photo(open(chart, "rb"))
    else:
        await message.answer("Недостаточно данных для графика.")
