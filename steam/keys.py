
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


@dp.message_handler(commands=['steam_keys'])
async def get_keys(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Вы можете получить ключи Steam в данном чате. Выберите один из вариантов:",
                           parse_mode="Markdown",
                           reply_markup=static.steam_keys_keyboard)
    

@dp.callback_query_handler(lambda call: call.data.startswith('steam'))
async def buy_steam(call: types.CallbackQuery):
    product_id = int(call.data.split("|")[-1])

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
        await bot.send_message(call.from_user.id, "Продукт не найден.")
        return
    if response.status_code == 200:
        product_name = data["product"]["name"]
        product_price = data["product"]["price"]
        product_description = data["product"]["info"]

        language = re.search(r'Язык(?:и)?: (.+?)<br />', product_description).group(1)
        activation_region = re.search(r'Регион(?: активации)?: (.+?)<br />', product_description).group(1)

        with io.BytesIO(image_data) as image_stream:
            await bot.send_photo(call.from_user.id,
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
        await bot.send_message(call.from_user.id, "Произошла ошибка при получении данных о продукте.")


@dp.callback_query_handler(lambda call: call.data.startswith('game_key'))
async def game_key(call: types.CallbackQuery):
    product_id = int(call.data.split("|")[-1])
    logger.warning(f"id: {product_id}")
    url = "https://shop.digiseller.ru/xml/create_invoice.asp"
    data = {
        "digiseller.request": f"""<digiseller.request><id_good>{product_id}</id_good><wm_id>{WM_ID}</wm_id><email>{EMAIL}</email><id_partner>{ID_PARTHNER}</id_partner><curr>{CURR}</curr><lang>{LANG}</lang></digiseller.request>"""
    }
    response = requests.post(url, data=data)
    response_data = response.text

    logger.info(f'ОТВЕТ: {response_data}')

    await bot.send_message(call.from_user.id, response_data)

