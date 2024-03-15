
from asyncpg import Record

from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler


from loguru import logger

from config import bot
from bases import pool


async def create_user(message: types.Message, media: int = 10):
    async with pool.acquire() as conn:
        check_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE user_id = $1 ",
                                 message.from_user.id)
        if check_users == 0:
            now = datetime.now()
            await conn.execute("INSERT INTO users (user_id, username, datetime) VALUES ($1, $2, $3)",
                                message.from_user.id, message.from_user.username, now)
            logger.info(f"""[Регистрация][ID - {int(message.from_user.id)}][@{message.from_user.username}]""")
            return True
        else:
            return False


class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        super(LoggingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, *args):
        #Проверка на регистрацию
        await create_user(message)
        logger.info(f"""Пидор {message.from_user.id} @{message.from_user.username} написал {message.text}""")

    async def on_process_callback_query(self, call: types.CallbackQuery, *args):
        identifier: str = f'[ID: {call["from"].id}]'
        if call["from"].username:
            identifier: str = f"""[ID: {call["from"].id}][@{call['from'].username}]"""

        logger.info(f"{identifier} Нажатие на кнопку {call.data!r}")

def rate_limit(key=None):
    def decorator(func):
        setattr(func, 'throttling_rate_limit', DEFAULT_RATE_LIMIT)
        if key:
            setattr(func, 'throttling_key', key)
        return func
    return decorator

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit

        self.prefix = key_prefix
        self.time_updates = {}

        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if message.is_command():
            return

        if data.get("raw_state") is not None:
            return

        limit = 7

        if message.from_user.id not in self.time_updates.keys():
            self.time_updates[message.from_user.id] = datetime.now()
            return

        delta_seconds = (
            datetime.now() -
            self.time_updates[message.from_user.id]).seconds

        if limit > delta_seconds:
            await bot.send_message(
                message["from"].id,
                f"Сообщение не доставлено, так как вы пишите слишком часто!\n\nНапишите еще раз через {int(limit - delta_seconds)} сек.")
            raise CancelHandler()

        self.time_updates[message.from_user.id] = datetime.now()

def configure_dp(dp: Dispatcher):
    dp.middleware.setup(LoggingMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
