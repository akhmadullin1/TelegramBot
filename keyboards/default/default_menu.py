from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu_start = ReplyKeyboardMarkup(
keyboard = [
        [
            KeyboardButton(text="Создать задачу"),
            KeyboardButton(text="Список задач"),
            KeyboardButton(text="Удалить задачу")
        ]
], resize_keyboard=True
)

