from aiogram.dispatcher.filters.state import State, StatesGroup


class TaskForm(StatesGroup):
    text = State()
    time = State()
