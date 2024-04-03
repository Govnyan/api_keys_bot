
import requests
import io
import re

from aiogram import types
from asyncpg import Record
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from bases import pool
from config import dp, bot


async def parse_keys(user_id):
    product_id = 3666463
    url = f"https://api.digiseller.ru/api/products/{product_id}/data"
    headers = {
        "Accept": "application/json"
    }
    params = {
        "currency": "RUB"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    logger.info(f'СТАТУС: {response.status_code}')

    if response.status_code == 404:
        await bot.send_message(user_id, "Продукт не найден.")
        return
    if response.status_code == 200:
        product_name = data["product"]["name"]
        product_price = data["product"]["price"]
        product_description = data["product"]["info"]

        language = re.search(r'Язык: (.+?)<br />', product_description).group(1)
        release_date = re.search(r'Дата выпуска: (.+?)<', product_description).group(1)
        activation_region = re.search(r'Регион активации: (.+?)<br />', product_description).group(1)

        await bot.send_message(user_id, f"""
{product_name}
*Цена:* {product_price} ₽

*Описание*
*Дата выпуска:* {release_date}
*Язык:* {language}
*Регион активации:* {activation_region}
""", parse_mode="Markdown")
    else:
        await bot.send_message(user_id, "Произошла ошибка при получении данных о продукте.")

    url_image = "http://graph.digiseller.ru/img.ashx"
    params = {
        "id_d": f"{product_id}",
        "w": "200",
        "h": "150",
        "crop": "true"
    }

    response_image = requests.get(url_image, params=params)
    image_data = response_image.content

    with io.BytesIO(image_data) as image_stream:
        await bot.send_photo(user_id,
                             photo=image_stream,
                             caption="Фото")


@dp.message_handler(commands=['steam_keys'])
async def get_keys(message: types.Message):
    await parse_keys(message.from_user.id)


