
from aiogram import types
from asyncpg import Record
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from config import dp, bot
from bases import pool

from middleware import rate_limit
from extradition.extradition import *
from payment.payment import *
from admins.admins import *
from steam.keys import *

import static

class Keys(StatesGroup):
    key = State()

def escape_md(word: str) -> str:
    ESCAPE_SYMBOLS = ("`", "*", "_")
    for symbol in ESCAPE_SYMBOLS:
        word = word.replace(symbol, rf"\{symbol}")

    return word


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           static.START_MESSAGE,
                           reply_markup=static.start_keyboard,
                           parse_mode="Markdown")


@dp.message_handler(content_types=types.ContentTypes.TEXT)
@rate_limit()
async def text(message: types.Message):
    await start(message)


@dp.message_handler(commands=['key'])
@dp.callback_query_handler(lambda call: call.data == 'key')
async def key(message: types.Message):
    await Keys.key.set()
    await bot.send_message(message["from"].id,
                           static.KEY_SET,
                           parse_mode="Markdown",
                           reply_markup=static.cancel_keyboard)

@dp.message_handler(state=Keys.key)
async def count_key(message: types.Message, state: FSMContext):
    try:
        key_count = int(message.text)
    except ValueError:
        await bot.send_message(message.from_user.id,
                               static.KEY_ERROR_1,
                               parse_mode="Markdown",
                               reply_markup=static.cancel_keyboard)
        return

    if key_count < 1 or key_count > 30:
        await bot.send_message(message.from_user.id,
                               static.KEY_ERROR_2,
                               parse_mode="Markdown",
                               reply_markup=static.cancel_keyboard)
        return

    await state.finish()
    if key_count < 10:
        money = key_count * 14
        KEY_MESSAGE = f"""Ключей выбрано: <b>{key_count}</b>, к оплате: <b>{money}₽</b>"""
    else:
        money_1 = key_count * 14
        money = key_count * 12
        KEY_MESSAGE = f"""Ключей выбрано: <b>{key_count}</b>, к оплате: <s>{money_1}₽</s> <b>{money}₽</b>"""

    payment_keyboard = types.InlineKeyboardMarkup()
    payment_keyboard.add(
        types.InlineKeyboardButton("💳Оплатить",
        callback_data=f"{money}|{key_count}|payment"))

    logger.info(f"""[BUYING KEYS][ID: {message.from_user.id}][@{message.from_user.username}][COUNT: {key_count}]""")
    await bot.send_message(message["from"].id,
                            KEY_MESSAGE,
                            parse_mode="HTML",
                            reply_markup=payment_keyboard)



@dp.callback_query_handler(lambda call: call.data == 'cancel', state=[Keys.key])
async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id,
                                    "Отмена")
    await state.finish()
    await start(callback_query)