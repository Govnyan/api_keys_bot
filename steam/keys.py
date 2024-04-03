
import requests
import io

from aiogram import types
from asyncpg import Record
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from bases import pool
from config import dp, bot

from . import static


async def parse_keys(user_id):
    product_id = 3666463
    url = f"https://api.digiseller.ru/api/products/{product_id}/data"
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    
    logger.info(f'СТАТУС: {response.status_code}')

    if response.status_code == 404:
        await bot.send_message(user_id, "Продукт не найден.")
        return
    if response.status_code == 200:
        product_name = data["product"]["name"]
        product_price = data["product"]["price"]
        product_description = data["product"]["info"]

        await bot.send_message(user_id, f"""
Название: {product_name}
Цена: {product_price}
Описание: {product_description}""")
    else:
        await bot.send_message(user_id, "Произошла ошибка при получении данных о продукте.")

    '''url = "http://graph.digiseller.ru/img.ashx"
    # Параметры запроса
    params = {
        "id_d": "2029463",
        "w": "200",
        "h": "150",
        "crop": "true"
    }

    # Отправляем GET-запрос и получаем изображение
    response = requests.get(url, params=params)
    image_data = response.content

    # Отправляем изображение через bot.send_photo
    with io.BytesIO(image_data) as image_stream:
        await bot.send_photo(chat_id=user_id, photo=image_stream, caption="Описание изображения")'''


@dp.message_handler(commands=['steam_keys'])
async def get_keys(message: types.Message):
    await parse_keys(message.from_user.id)


