from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_inline_keyboard(list_tasks):
    inline_keyboard = InlineKeyboardMarkup()
    for task in list_tasks:
        result_text = '{task_text}. {task_state} '.format(task_text=task[2], task_state="(Выделено)" if task[4] else "")
        inline_keyboard.add(InlineKeyboardButton(text=result_text, callback_data=task[0]))
    return inline_keyboard