from aiogram import types

ADMIN = "Админ панель 👀\n\nВыберите пункт меню:"

ADD_KEY = "Копируй ключи сюда:"

admin_keyboard = types.InlineKeyboardMarkup()
admin_keyboard.add(
    types.InlineKeyboardButton(
    "Статистика бота 📈",
    callback_data="stats"))
admin_keyboard.add(
    types.InlineKeyboardButton(
    "Рассылка ✉️",
    callback_data="say_all"))
admin_keyboard.add(
    types.InlineKeyboardButton(
        "Добавить ключи🔑",
        callback_data="add_keys"
    ))
admin_keyboard.add(
    types.InlineKeyboardButton(
        "Забрать 20%💰",
        callback_data="get_money"
    ))

cancel_admin_keyboard = types.InlineKeyboardMarkup()
cancel_admin_keyboard.add(
    types.InlineKeyboardButton("❌Отмена",
    callback_data="cancel_admin"))
