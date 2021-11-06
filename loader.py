import logging
import sqlite3
import config
from aiogram import Bot, Dispatcher, types
from db.models import create_table_tasks, create_table_users
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

conn = sqlite3.connect("./db/"+config.BD_NAME)
cur = conn.cursor()
conn.execute("PRAGMA foreign_keys = ON")
create_table_users(cur, conn)
create_table_tasks(cur, conn)


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )