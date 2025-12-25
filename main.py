import asyncio
import os
from collections import defaultdict
from datetime import date

import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
PASSWORD = "150799"

# ================== STORAGE ==================
balances = defaultdict(float)
daily_stats = defaultdict(lambda: defaultdict(float))
monthly_stats = defaultdict(lambda: defaultdict(float))

authorized_users = set()
waiting_for_amount = {}
operation_type = {}

# ================== KEYBOARD ==================
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="доход"), KeyboardButton(text="расход")],
        [KeyboardButton(text="день"), KeyboardButton(text="месяц"), KeyboardButton(text="график")]
    ],
    resize_keyboard=True
)

# ================== BOT ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== HANDLERS ==================
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Использование бота возможно после ввода уникального пароля.\n"
        "Пожалуйста, вводите пароль:"
    )


@dp.message(F.text == PASSWORD)
async def correct_password(message: Message):
    authorized_users.add(message.from_user.id)
    await message.answer(
        "Доступ разрешен. Доходы и расходы вводить с помощью команд!",
        reply_markup=keyboard
    )


@dp.message(lambda m: m.from_user.id not in authorized_users)
async def denied(message: Message):
    await message.answer("Доступ ограничен!")


@dp.message(F.text.in_(["доход", "расход"]))
async def choose_operation(message: Message):
    waiting_for_amount[message.from_user.id] = True
    operation_type[message.from_user.id] = message.text
    await message.answer("Введите сумму:")


@dp.message()
async def process_amount(message: Message):
    user_id = message.from_user.id

    if not waiting_for_amount.get(user_id):
        return

    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    today = date.today().isoformat()
    month = today[:7]

    if operation_type[user_id] == "расход":
        amount = -amount

    balances[user_id] += amount
    daily_stats[user_id][today] += amount
    monthly_stats[user_id][month] += amount

    balance = balances[user_id]
    sign = "+" if balance >= 0 else ""

    await message.answer(
        f"{sign}{balance:.2f} BYN",
        reply_markup=keyboard
    )

    waiting_for_amount[user_id] = False


@dp.message(F.text == "день")
async def day_balance(message: Message):
    today = date.today().isoformat()
    amount = daily_stats[message.from_user.id].get(today, 0.0)
    await message.answer(f"Дневной баланс: {amount:.2f} BYN")


@dp.message(F.text == "месяц")
async def month_balance(message: Message):
    month = date.today().isoformat()[:7]
    amount = monthly_stats[message.from_user.id].get(month, 0.0)
    await message.answer(f"Месячный баланс: {amount:.2f} BYN")


@dp.message(F.text == "график")
async def graph(message: Message):
    data = daily_stats[message.from_user.id]

    if not data:
        await message.answer("Недостаточно данных для графика.")
        return

    dates = sorted(data.keys())
    values = [data[d] for d in dates]

    plt.figure()
    plt.plot(dates, values)
    plt.xticks(rotation=45)
    plt.title("Дневной баланс")
    plt.tight_layout()

    filename = f"chart_{message.from_user.id}.png"
    plt.savefig(filename)
    plt.close()

    await message.answer_photo(open(filename, "rb"))


# ================== START ==================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
