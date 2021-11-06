import asyncio
from loader import bot
from aiogram import executor
from handlers import dp
from handlers.users.to_do_list import notify


async def on_shutdown():
    await bot.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notify())

    executor.start_polling(dp, on_shutdown=on_shutdown)