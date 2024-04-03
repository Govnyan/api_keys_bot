
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import argparse
import uvloop
import os
from loguru import logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

# Переменные окружения, без которых программа не запустится
ENV = ("user", "host", "password", "dbname", "token")

class args:
    for env in ENV:
        assert env in os.environ, f"Переменная '{env}' не задана!"

    user: str = os.environ.get("user")
    host: str = os.environ.get("host")
    password: str = os.environ.get("password")
    dbname: str = os.environ.get("dbname")

    token: str = os.environ.get("token")
    yoomoney: str = os.environ.get("yoomoney")
    yoomoney_id: str = os.environ.get("yoomoney_id")

    parser = argparse.ArgumentParser()

    #parser.add_argument("--user")

    args = parser.parse_args()


args = args()


TOKEN = args.token
OPEN_TOKEN = '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'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage(), loop=loop)

KEY_PATH = '/home/data/maks/keys/keys.txt'
SOLD_KEY_PATH = '/home/data/maks/keys/'

WM_id = "110077631651"
