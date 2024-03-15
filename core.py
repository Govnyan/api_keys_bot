
from aiogram import executor
from config import dp, loop
from loguru import logger

from main import *

from middleware import configure_dp

configure_dp(dp)

if __name__ == '__main__':
    logger.info("Бот запускается по Long-Polling")
    executor.start_polling(dp, skip_updates=True, loop=loop)
