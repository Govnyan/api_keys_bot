from aiogram import types


steam_keys_keyboard = types.InlineKeyboardMarkup()
steam_keys_keyboard.add(
    types.InlineKeyboardButton("DREAM PINBALL 3D",
                               callback_data="steam|3666463"))
steam_keys_keyboard.add(
    types.InlineKeyboardButton("KINGDOM COME: DELIVERANCE ROYAL EDITION",
                               callback_data="steam|4110572"))
steam_keys_keyboard.add(
    types.InlineKeyboardButton("MASS EFFECT LEGENDARY",
                               callback_data="steam|3541881"))