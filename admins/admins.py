
from aiogram import types
from asyncpg import Record
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from bases import pool
from config import dp, bot, KEY_PATH, SOLD_KEY_PATH

from . import static

class AddKeys(StatesGroup):
    add_key = State()

async def check_admin(user_id: int):
    async with pool.acquire() as conn:
        record = await conn.fetchval("SELECT user_id FROM admins WHERE user_id = $1",
                                     user_id)
        if record:
            return True
        else:
            return False


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if not await check_admin(message["from"].id):
        return
    else:
        await bot.send_message(message["from"].id,
                               static.ADMIN,
                               reply_markup = static.admin_keyboard,
                               parse_mode = "Markdown")


@dp.callback_query_handler(lambda call: call.data == 'add_keys')
async def add_key(call: types.CallbackQuery):
    await AddKeys.add_key.set()
    await bot.send_message(call.from_user.id,
                           static.ADD_KEY,
                           parse_mode="Markdown",
                           reply_markup=static.cancel_admin_keyboard)


@dp.message_handler(state=AddKeys.add_key)
async def add_count(message: types.Message, state: FSMContext):
    add_keys = message.text.split('\n')
    added_keys = 0

    with open(KEY_PATH, 'a') as file:
        for key in add_keys:
            file.write(f"{key}\n")
            added_keys += 1

    await bot.send_message(message["from"].id,
                            f"Ключей добавлено: *{added_keys}*",
                            parse_mode="Markdown")

    await state.finish()

@dp.callback_query_handler(lambda call: call.data == 'cancel_admin', state=[AddKeys.add_key])
async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id,
                                    "Отмена")
    await state.finish()


@dp.callback_query_handler(lambda call: call.data == 'get_money')
async def get_money(call: types.CallbackQuery):
    sticker_id = "CAACAgIAAxkBAAJIw2X51TstxB773Oad0Uic7r9MjuI5AAKwHwACydrQSoqdo0Ms-4qgNAQ"
    await bot.send_sticker(call.from_user.id,
                           sticker_id)


@dp.callback_query_handler(lambda call: call.data == 'stats')
async def stats(call: types.CallbackQuery):
    async with pool.acquire() as conn:
        record = await conn.fetchrow("SELECT SUM(amount) as money, SUM(count) as count FROM buy")

        sold_keys = record['count']
        money = record['money']


        with open(KEY_PATH, 'r') as file:
            lines = file.readlines()

        all_keys = len(lines)
        await bot.send_message(call.from_user.id,
                            f"""Статистика📈

📊*Остаток ключей*: {all_keys} шт.,
♻️*Продано*: {sold_keys} шт.,
💵*Заработано*: {money} ₽
""",
                            parse_mode="Markdown")
