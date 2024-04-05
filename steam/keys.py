
import requests
import io
import re
import math

from aiogram import types
from asyncpg import Record
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from bases import pool
from config import dp, bot, WM_ID, EMAIL, ID_PARTHNER, CURR, LANG

from . import static


async def parse_keys(user_id, product_id):
    url = f"https://api.digiseller.ru/api/products/{product_id}/data"
    headers = {
        "Accept": "application/json"
    }
    params = {
        "currency": "RUB"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    url_image = "http://graph.digiseller.ru/img.ashx"
    params_image = {
        "id_d": f"{product_id}"
    }
    response_image = requests.get(url_image, params=params_image)
    image_data = response_image.content

    get_steam_keyboard = types.InlineKeyboardMarkup()
    get_steam_keyboard.add(
        types.InlineKeyboardButton("Получить",
                                callback_data=f"game_key|{product_id}"))

    logger.info(f'СТАТУС: {response.status_code}')

    if response.status_code == 404:
        await bot.send_message(user_id, "Продукт не найден.")
        return
    if response.status_code == 200:
        product_name = data["product"]["name"]
        product_price = data["product"]["price"]
        product_description = data["product"]["info"]

        language = re.search(r'Язык(?:и)?: (.+?)<br />', product_description).group(1)
        activation_region = re.search(r'Регион(?: активации)?: (.+?)<br />', product_description).group(1)

        with io.BytesIO(image_data) as image_stream:
            await bot.send_photo(user_id,
                                photo=image_stream,
                                caption=f"""
{product_name}
*Цена:* {math.ceil(product_price)} ₽

*Описание*

*Язык:* {language}
*Регион активации:* {activation_region}
""",
                                parse_mode="Markdown",
                                reply_markup=get_steam_keyboard)
    else:
        await bot.send_message(user_id, "Произошла ошибка при получении данных о продукте.")

async def send_wm(id_good, wm_id, email, id_partner, curr, lang):
    url = "https://shop.digiseller.ru/xml/create_invoice.asp"
    data = {
        "digiseller.request": f"<digiseller.request><id_good>{id_good}</id_good><wm_id>{wm_id}</wm_id><email>{email}</email><id_partner>{id_partner}</id_partner><curr>{curr}</curr><lang>{lang}</lang></digiseller.request>"
    }
    response = requests.post(url, data=data)
    response_data = response.text

    return response_data


@dp.message_handler(commands=['steam_keys'])
async def get_keys(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы можете получить ключи Steam в данном чате. Выберите один из вариантов:",
                           parse_mode="Markdown",
                           reply_markup=static.steam_keys_keyboard)
    

@dp.callback_query_handler(lambda call: call.data.startswith('steam'))
async def buy_steam(call: types.CallbackQuery):
    product_id = int(call.data.split("|")[-1])
    await parse_keys(call.from_user.id, product_id)


@dp.callback_query_handler(lambda call: call.data.startswith('game_key'))
async def game_key(call: types.CallbackQuery):
    product_id = int(call.data.split("|")[-1])
    data = await send_wm(2142729, WM_ID, EMAIL, ID_PARTHNER, CURR, LANG)

    await bot.send_message(call.from_user.id, data)

    
