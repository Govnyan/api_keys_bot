import os

from aiogram import types
from loguru import logger
from datetime import datetime, date

from config import dp, bot, KEY_PATH, SOLD_KEY_PATH
from bases import pool

today = date.today()

async def spend_keys(user_id, key_count) -> bool:
    async with pool.acquire() as conn:
        key_balance = await conn.fetchval("SELECT key_balance FROM users WHERE user_id = $1",
                                    user_id)
        if key_balance >= key_count:
            await conn.execute("UPDATE users SET key_balance = $1 WHERE user_id = $2",
                                key_balance - key_count,
                                user_id)
            return True
        else:
            return False

def get_api_keys(key_path, sold_keys_path, count, user_id):
    with open(key_path, 'r') as file:
        lines = file.readlines()

    if len(lines) < count:
        return None  

    keys_to_give = lines[:count]
    remaining_keys = lines[count:]

    sold_keys = f'{sold_keys_path}{user_id}/'
    os.makedirs(sold_keys, exist_ok=True)
    sold_count = len([name for name in os.listdir(sold_keys) if os.path.isfile(os.path.join(sold_keys, name)) and name.startswith(str(today)) and name.endswith('.txt')])
    sold_keys_user = os.path.join(sold_keys, f'{today}_{sold_count + 1}.txt')

    with open(key_path, 'w') as file:
        file.writelines(remaining_keys)

    with open(sold_keys_user, 'a') as file:
        file.writelines(keys_to_give)

    return keys_to_give


@dp.callback_query_handler(lambda call: call.data.startswith('get_key'))
async def buy(call: types.CallbackQuery):
    keys_count = int(call.data.split("|")[1])
    amount = int(call.data.split("|")[-1])
    async with pool.acquire() as conn:
        if await spend_keys(call.from_user.id, keys_count):
            keys_to_give = get_api_keys(KEY_PATH, SOLD_KEY_PATH, keys_count, call.from_user.id)
            if not keys_to_give:
                await call.message.edit_text("❌Недостаточно ключей в базе. Пополните их, пожалуйста!")
                return

            formatted_keys = "\n".join(keys_to_give) 
            await conn.execute("INSERT INTO buy (user_id, amount, name, count, date) VALUES ($1, $2, $3, $4, $5)",
                                call.from_user.id,
                                amount,
                                'Ключи выданы',
                                keys_count,
                                datetime.now())
            await call.message.edit_text(f"""✅Спасибо за покупку! По всем вопросам обращайтесь в службу поддержки.
❗ ❗ ❗ ПРОЧИТАЙ!

*1*. Перед тем как выполнять вход в аккаунт, обязательно проверь включен ли *VPN*!

*2*. Если ты выполнил вход без включенного VPN, твой браузер попадает в черный список входа OpenAI! Это решается сменой браузера или можно попробовать очистить кэш, куки, использовать режим инкогнито.

*3*. Далее когда вы уже будете авторизованы и откроете страницу чата без VPN, то браузер не попадет в черный список, но без VPN чат-бот работать не будет.

P.S: В общем главное обращать внимание на VPN когда вы вводите данные для авторизации, после авторизации уже ничего критичного не будет.

🔰Ваши аккаунты:""",
                                        parse_mode="Markdown")
            await bot.send_message(call.from_user.id,
                                   f"{formatted_keys}",
                                   parse_mode="Markdown")
        else:
            await call.message.edit_text("❌Недостаточно средств! Пополните баланс!")
