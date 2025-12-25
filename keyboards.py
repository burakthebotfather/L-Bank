from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="доход"), KeyboardButton(text="расход")],
        [KeyboardButton(text="день"), KeyboardButton(text="месяц"), KeyboardButton(text="график")]
    ],
    resize_keyboard=True
)
