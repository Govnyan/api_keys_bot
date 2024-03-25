from aiogram import types

#main
START_MESSAGE = """⭐️В продаже доступны OpenAI (GPT) аккаунты с 5$ на счету. 
Аккаунты персональные и доступны только Вам 
Стоимость одного аккаунта *14 ₽*.
⚡️При покупке *от 10 аккаунтов* сумма будет составлять *12 ₽* за аккаунт.

🛒 После покупки вы получите:
✅ Данные для входа в личный кабинет в формате: *LOGIN:PASSWORD:APIKEY*.
✅ ChatGPT готов к использованию сразу после покупки.
*Для входа в аккаунт VPN обязателен, для использования API ключа VPN НЕ Обязателен.*

❗ ❗ ❗ Важная информация!
✅ Мы не несем ответственности за любые действия, совершенные Вами на аккаунте, которые могут привести к его блокировке, ограничению или другим негативным последствиям.
✅ При наличии абсолютно любых вопросов/жалоб по поводу заказа, сообщите нам об этом в службу поддержки, и мы постараемся уладить Ваш вопрос."""

KEY_SET = "Введите желаемое количество."
KEY_ERROR_1 = "*Ошибка!* Введите число."
KEY_ERROR_2 = """*Ошибка!* Введите число от *1* до *30*.

В наличии только 30 ключей.
Могу сделать любое количество, напишите в [службу поддержки GPT API store](https://t.me/GPT_api_keys_support_bot)."""

start_keyboard = types.InlineKeyboardMarkup()
start_keyboard.add(
    types.InlineKeyboardButton("✅Получить аккаунт(5$) + API ключ",
    callback_data="key"))

cancel_keyboard = types.InlineKeyboardMarkup()
cancel_keyboard.add(
    types.InlineKeyboardButton("❌Отмена",
    callback_data="cancel"))

payment_keyboard = types.InlineKeyboardMarkup()
payment_keyboard.add(
    types.InlineKeyboardButton("💳Оплатить",
    callback_data="payment"))
