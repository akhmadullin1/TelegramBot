"""Основные обработчики для работы бота.
    Здесь находится основная логика"""

import datetime
import asyncio

from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import Message,  CallbackQuery

from keyboards.default import menu_start
from keyboards.inline import get_inline_keyboard
from loader import dp, conn, cur, bot
from db.models import (set_user, get_user, del_user,
                       set_task, get_tasks, get_tasks_time_not_null, del_task, del_checked_tasks, change_check_task)
from handlers.users.states import TaskForm


@dp.message_handler(commands=['start'])
async def start(message: Message):
    set_user(cur, conn, message.from_user.id, message.from_user.first_name)  # Создаем запись о пользователе
    await message.answer("Меню под полем ввода открыто", reply_markup=menu_start)


@dp.message_handler(commands=['delete_me'])
async def delete_me(message: Message):
    del_user(cur, conn, message.from_user.id)  # Удаляем запись о пользователе и все его задачи
    await bot.send_photo(message.chat.id, photo=open('static/pictures/zahodi.jpg', 'rb'))
    await message.answer("Мы тебя ждем, <b>{user_name}</b> :)".format(user_name=message.from_user.first_name),
                         reply_markup=menu_start)


@dp.message_handler(commands=['info'])
async def info(message: Message):
    await message.answer("<b>Информация:</b>\n "
                         "/start - начало работы с программой, создаем запись о пользователе.\n"
                         "/menu - вызов меню с кнопками "
                         "<b>Создать задачу</b>, <b>Список задач</b>, <b>Удалить задачу</b>.\n"
                         "Кнопка <b>Создать задачу</b> создает задачу, если существует запись пользователя в БД.\n"
                         "Кнопка <b>Список задач</b> открывет inline-menu текущих задач, по нажатию на которые "
                         "можно сделать задачу выделенной.\n"
                         "Кнопка <b>Удалить задачу</b> удаляет выделенные задачи.\n"
                         "/delete_me - удаляет запись пользователя в БД.")


@dp.message_handler(commands=['menu'])
async def show_menu(message: Message):
    await message.answer("Меню под полем ввода открыто", reply_markup=menu_start)


@dp.callback_query_handler(lambda call: call.data)
async def show_tasks(call: CallbackQuery):
    list_tasks = get_tasks(cur, call.from_user.id)
    for task in list_tasks:  # Среди задач пользователя выводим ту, которую он нажал
        if task[0] == int(call.data):
            change_check_task(cur, conn, task[0], call.from_user.id)  # При нажатии на задачу она меняет свое состояние
            data_task = "<b>Текст задачи:</b>\n " \
                        "{task_text}\n\n " \
                        "<b>Время исполнения:</b>\n " \
                        "{task_time}\n\n " \
                        "<u><b>{task_check}</b></u>".format(task_text=task[2], task_time=task[3],
                                                            task_check="Не выделено" if task[4] else "Выделено")
            await call.message.answer(data_task)
            await call.answer()


async def notify():  # Напоминание о задачи, у которой подошло время выполнения
    while True:
        task_list = get_tasks_time_not_null(cur)  # Берем все задачи, у который оределено время исполнения
        for task in task_list:
            if task[3] == datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00'):
                data_task = "<b>Текст задачи:</b>\n " \
                            "{task_text}\n\n " \
                            "<b>Время исполнения:</b>\n " \
                            "{task_time}\n\n " \
                            "<u><b>Исполнена и удалена</b></u>".format(task_text=task[2], task_time=task[3][0:-3])
                del_task(cur, conn, task[0], task[1])
                await bot.send_message(task[1], data_task)

        await asyncio.sleep(1)


@dp.message_handler(Text(equals=["Создать задачу"]))
async def create_task(message: Message):
    if get_user(cur, message.from_user.id):
        await message.reply("Введите текст задачи")
        await TaskForm.text.set()  # Устанавливаем текст в машину состояний
    else:
        await message.reply("Вашей записи нет в БД! Введите команду /start, чтобы создать запись.")


@dp.message_handler(state=TaskForm.text)
async def state_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)  # Обновляем текст
    await message.answer("Введите время напоминания Y-m-d H:M или нет")
    await TaskForm.time.set()  # Устанавливаем время в машину состояний


@dp.message_handler(state=TaskForm.time)
async def state_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)  # Обновляем время
    data = await state.get_data()  # Получаем все данные машины состояний
    time_exist = False
    if data.get("time").lower() != 'нет':
        try:
            date_time_obj = datetime.datetime.strptime(data.get("time"), '%Y-%m-%d %H:%M')  # Приводим время к виду
            time_exist = True
            try:
                delta = date_time_obj - datetime.datetime.now()  # Разница между временем напоминания и текущим
                if delta.days < 0:
                    raise ValueError
            except ValueError:
                await message.answer("Время уже прошло, задача создастся без напоминания")
                time_exist = False

        except ValueError:
            await message.answer("Неправильно введена дата и время, задача создастся без напоминания")

    if time_exist:
        set_task(cur, conn, message.from_user.id, data.get("text"),
                 datetime.datetime.strptime(data.get("time"), '%Y-%m-%d %H:%M'))

    else:
        set_task(cur, conn, message.from_user.id, data.get("text"), None)

    await message.answer("Задача создана")
    await state.finish()


@dp.message_handler(Text(equals=["Список задач"]))
async def show_tasks(message: Message):
    list_tasks = get_tasks(cur, int(message.from_user.id))
    await message.answer('Ваш список задач:', reply_markup=get_inline_keyboard(list_tasks))


@dp.message_handler(Text(equals=["Удалить задачу"]))
async def show_tasks(message: Message):
    del_checked_tasks(cur, conn, message.from_user.id)
    await message.answer("Все выделенные задачи удалены!")
