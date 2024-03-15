import random
import string

from typing import Union
from aiogram import types
from asyncpg import Record
from aiogram.dispatcher.filters import Command

from bases import pool

from config import dp, bot, args, KEY_PATH
from datetime import datetime, date, timedelta

from yoomoney import Quickpay
from yoomoney import Client


token = args.yoomoney

def random_string(length) -> str:
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


@dp.callback_query_handler(lambda call: call.data.endswith("payment"))
@dp.message_handler(Command("payment"))
async def pay_handler(call: Union[types.Message, types.CallbackQuery]):
    money = int(call.data.split("|")[0])
    keys_count = int(call.data.split("|")[1])
    async with pool.acquire() as conn:

        with open(KEY_PATH, 'r') as file:
            lines = file.readlines()

        remains = len(lines)

        if remains < keys_count:
            await bot.send_message(call.from_user.id,
                                   f"""😢Нет в наличии.
Осталось {remains} шт.
Для получения аккаутов напишите нам в [службу поддержки GPT API store](https://t.me/GPT_api_keys_support_bot)""",
                                   parse_mode="Markdown")
            return

        code = random_string(30)

        quickpay = Quickpay(
                    receiver=f"f{args.yoomoney_id}",
                    quickpay_form="shop",
                    targets="Sponsor this project",
                    paymentType="SB",
                    sum=money,
                    label=code
                    )

        await conn.execute("INSERT INTO payment(receive, date, code, user_id, waiting, success) VALUES($1, $2, $3, $4, TRUE, FALSE)",
                            money, datetime.now(), code, call.from_user.id)
        payment_keyboard = types.InlineKeyboardMarkup()
        payment_keyboard.add(
            types.InlineKeyboardButton(
                "Оплатить",
                url=quickpay.base_url))

        payment_keyboard.add(
                types.InlineKeyboardButton(
                    "Проверить оплату",
                    callback_data=f"check_payment|{keys_count}|{code}"))

        await call.message.edit_text(f"🟢 Платёж создан и ждет оплаты. \
    Сумма пополнения: *{money}* RUB\
    \n\n❗️_Деньги поступят только после нажатия на кнопку \"Проверить платеж\"_",
                                    parse_mode="Markdown", reply_markup=payment_keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith("check_payment"))
async def check_payment_handler(call):
    code = call.data.split("|")[-1]
    keys_count = int(call.data.split("|")[1])
    async with pool.acquire() as conn:
        record: Record = await conn.fetchrow("SELECT waiting, success, receive FROM payment WHERE code = $1", code)
        waiting = record.get('waiting')
        success = record.get('success')
        receive = record.get('receive')

        store_keyboard = types.InlineKeyboardMarkup()
        store_keyboard.add(types.InlineKeyboardButton("✅Получить", callback_data=f"get_key|{keys_count}|{receive}"))

        if waiting and not success:
            client = Client(token)
            history = client.operation_history(label=code)
            for operation in history.operations:
                if operation.status == 'success':
                    success = True
                    amount = operation.amount

        if success:
            await conn.execute("UPDATE payment SET waiting=FALSE, success=TRUE WHERE user_id=$1 AND code=$2",
                                call.from_user.id, code)

            await conn.execute("UPDATE users SET balance=balance + $1 WHERE user_id=$2",
                                receive,
                                call.from_user.id)
            
            await conn.execute("UPDATE users SET key_balance=key_balance + $1 WHERE user_id=$2",
                                keys_count,
                                call.from_user.id)

            await call.message.edit_text(f"✅ {receive} ₽ зачислены!\
                                            \nТеперь вы можете получить товар.", reply_markup=store_keyboard)

            now = date.today()
            tomorrow = now + timedelta(days=1)

            admins = await conn.fetch("SELECT user_id FROM admins")
            today_receive = await conn.fetch("SELECT receive FROM payment WHERE date > $1 AND date < $2 AND waiting=FALSE AND success=TRUE",
                                                now, tomorrow)
            today_money = 0
            for money in today_receive:
                today_money += money[0]

            if admins:
                for admin in admins:
                    await bot.send_message(admin[0], f"Опааа, лавандосики)\
                                            \nПополнение на *{receive:0.0f}* р\
                                            \nПополнение с вычетом комиссии *{amount}* р\
                                            \nЗа сегодня: *{today_money:0.0f}* р\
                                            \nUser: *{call.from_user.id}*",
                                                    parse_mode="Markdown")
            return
